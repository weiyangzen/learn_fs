# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_runtime_jit.c

## Purpose
`verifier_runtime_jit.c` is a BPF verifier/JIT selftest fixture converted from the older verifier runtime JIT test set. It validates runtime tail-call behavior for socket programs, especially how prog-array maps, tail-call target selection, fallback execution, loop limits, and map pointer provenance behave once programs are JITed and executed. The source is not a Ceph runtime component; it is kernel selftest input compiled into BPF object code and consumed by the BPF test harness.

## Important APIs, Types, and Functions
The file defines two `BPF_MAP_TYPE_PROG_ARRAY` maps, `map_prog1_socket` and `map_prog2_socket`, using libbpf CO-RE style map declaration macros such as `__uint`, `__array`, and `SEC(".maps")`. The maps are pre-populated with auxiliary socket programs: `dummy_prog_42_socket`, `dummy_prog_24_socket`, `dummy_prog_loop1_socket`, and `dummy_prog_loop2_socket`. Each test program is `__naked` and uses inline BPF assembly so the instruction stream is exact. The central helper dependency is `bpf_tail_call`, referenced with `__imm(bpf_tail_call)`, and the branch tests also use `offsetof(struct __sk_buff, cb[0])` through `__imm_const`.

## Control Flow
Auxiliary programs either return fixed values or tail-call back through one of the prog arrays before returning 41 on fallback. Test entrypoints set `r2` to a prog-array map pointer and `r3` to a tail-call key, call `bpf_tail_call`, then return a fallback value if the tail call does not transfer control. The branch variants write to and read from `__sk_buff->cb[0]` to make verifier-visible paths that choose different map/key combinations. The out-of-bounds, negative-index, and wider-than-32-bit index cases assert fallback or architecture-specific behavior.

## State and Persistence
Persistent state is limited to the two prog-array map definitions and their static initial `values` arrays. There is no file or network persistence. Runtime state is verifier state and tail-call counter state: the fixture expects loop prevention and counter semantics to keep recursive tail calls bounded.

## Dependencies and Integration Points
The file depends on `<linux/bpf.h>`, `<bpf/bpf_helpers.h>`, `bpf_misc.h`, libbpf section annotations, and the selftest loader that understands `__description`, `__success`, `__success_unpriv`, `__failure_unpriv`, `__msg_unpriv`, and `__retval`. It integrates with socket program execution and the verifier's unprivileged restrictions around map pointer abuse.

## Risks and Test Signals
Key risks are verifier/JIT regressions that let a non-prog-array map pointer reach `bpf_tail_call`, mishandle high or negative indices, or fail to preserve branch-specific map pointer identity. Test signals are explicit return contracts: valid calls return 42 or 24 from auxiliary programs, loops fall back to 41, missing or invalid targets fall back to 1 or 2, and unprivileged execution rejects different-map branch cases with `tail_call abusing map_ptr`.
