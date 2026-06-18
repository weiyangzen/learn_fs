# sources/distributed-fs/ceph-client/kernel/bpf/dispatcher.c

## Purpose
`dispatcher.c` implements the generic BPF dispatcher, a multiway branch code generator that replaces expensive indirect BPF program calls with generated direct calls when retpolines or indirect-call costs matter. A dispatcher tracks a bounded set of BPF programs and updates a trampoline/static-call target to point at generated dispatch code or a nop fallback.

## Important APIs, types, and functions
`bpf_dispatcher_change_prog()` is the public mutation entry point. Internal helpers find existing or free slots, add/remove program references, prepare the generated image through `arch_prepare_bpf_dispatcher()`, and publish updates with `__BPF_DISPATCHER_UPDATE()`. The weak `arch_prepare_bpf_dispatcher()` returns `-ENOTSUPP` unless an architecture supplies code generation.

## Control flow
Changing a program first ignores no-op `from == to`. Under the dispatcher mutex it lazily allocates one executable packed page and one writable executable buffer, initializes kallsyms metadata, records the previous program count, removes `from`, adds `to`, and if the set changed calls `bpf_dispatcher_update()`. Update chooses one half of the page as the new image, alternating halves when an existing image is live. It prepares code into the writable mirror, copies it into the RO+X image with `bpf_arch_text_copy()`, updates the static dispatcher target to the generated image or `bpf_dispatcher_nop_func`, then waits for an RCU grace period before allowing the old half to be reused.

## State and persistence behavior
The dispatcher stores program slots, per-slot user refcounts, total program count, generated image pointers, current image offset, mutex, and kallsyms state in `struct bpf_dispatcher` supplied by the caller. Program references are acquired with `bpf_prog_inc()` and released with `bpf_prog_put()`. Generated images persist until dispatcher teardown managed elsewhere.

## Dependencies and integration points
This file integrates with architecture-specific dispatcher generation, BPF JIT executable memory allocation (`bpf_prog_pack_alloc`, `bpf_jit_alloc_exec`), text patching, static calls/macros, kallsyms registration, and RCU synchronization. It expects the arch generator to consume an array of BPF function addresses and emit valid branch code for the target trampoline ABI.

## Risks and test signals
Risks include stale direct-call targets, use-after-free of BPF programs, text patch failure leaving an old dispatcher active, incorrect half-page alternation, and architecture generator ABI mismatch. Tests should add/remove duplicate programs, exhaust `BPF_DISPATCHER_MAX`, handle allocation and arch-prepare failures, verify program refcounts, ensure fallback to nop when the last program is removed, and stress concurrent readers while changing the dispatch set.
