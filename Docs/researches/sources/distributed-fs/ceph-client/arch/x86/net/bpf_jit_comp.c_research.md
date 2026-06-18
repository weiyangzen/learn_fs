# sources/distributed-fs/ceph-client/arch/x86/net/bpf_jit_comp.c

## Purpose
Implements the x86-64 eBPF JIT backend, including machine-code emission for BPF instructions, text patching for BPF calls and tail calls, exception-table metadata for fault-tolerant probe/arena accesses, BPF trampoline generation, dispatcher generation, private BPF stacks, and architecture feature declarations. It is a core integration point between the verifier-produced `struct bpf_prog`, x86 text patching, CFI/IBT, retpoline/SLS mitigations, BPF maps, kfunc calls, and fentry/fexit/fmod_ret trampoline execution.

## Important APIs, types, and functions
- `struct jit_context` carries offsets for cleanup and direct/indirect tail-call labels across JIT passes.
- `struct x64_jit_data` persists partially finalized subprogram JIT state across extra passes for BPF subprogram compilation.
- `bpf_int_jit_compile()` is the top-level compiler entry. It allocates address maps, performs convergence passes, allocates executable/RW image packs, fills extable storage, finalizes text, updates instruction pointers, and installs `prog->bpf_func`.
- `do_jit()` is the main BPF-to-x86 translation loop. It emits the prologue, iterates over every BPF instruction, maps BPF opcodes to x86 encodings, populates exception tables, and validates pass stability.
- `emit_prologue()`, `emit_return()`, `push_callee_regs()`, `pop_callee_regs()`, and private-stack helpers define BPF frame layout and ABI preservation.
- `emit_bpf_tail_call_indirect()`, `emit_bpf_tail_call_direct()`, `bpf_tail_call_direct_fixup()`, and `bpf_arch_poke_desc_update()` implement BPF tail-call fast paths and runtime target patching.
- `bpf_arch_text_poke()`, `__bpf_arch_text_poke()`, `bpf_arch_text_copy()`, and `bpf_arch_text_invalidate()` wrap x86 text poking for BPF-generated code.
- `ex_handler_bpf()` is the x86 exception handler for JITed probe memory and arena accesses.
- `arch_prepare_bpf_trampoline()`, `__arch_prepare_bpf_trampoline()`, `arch_bpf_trampoline_size()`, allocation/free helpers, and `invoke_bpf*()` generate BPF trampoline images.
- `arch_prepare_bpf_dispatcher()` emits a binary-search dispatcher for multiple program entry addresses.
- Feature hooks include `bpf_jit_supports_kfunc_call()`, `bpf_jit_supports_subprog_tailcalls()`, `bpf_jit_supports_percpu_insn()`, `bpf_jit_supports_exceptions()`, `bpf_jit_supports_private_stack()`, `bpf_jit_supports_arena()`, `bpf_jit_supports_ptr_xchg()`, `bpf_jit_supports_timed_may_goto()`, and `bpf_jit_supports_fsession()`.

## Control flow
Compilation starts only when `prog->jit_requested` is set. The compiler either resumes stored `aux->jit_data` for an extra subprogram pass or allocates `addrs[]` with an overestimated per-instruction layout. `do_jit()` is run repeatedly until program length converges; late passes enable padding so short/near jump choices stop oscillating. Once length is stable, a packed executable image and RW alias are allocated, with exception-table space appended after aligned code. A final pass copies emitted bytes into the RW image and validates that `addrs[]` did not change. Finalization copies/pokes RW bytes into executable text, applies direct tail-call fixups, fills jited line info, and publishes the function pointer offset by any CFI prefix.

Inside `do_jit()`, the prologue handles CFI/IBT, a patchable call slot, frame setup, stack allocation, tail-call counter layout, optional arena base in `r12`, and optional per-CPU private stack pointer in `r9`. Each BPF instruction emits into a temporary buffer, then its length is accumulated into `addrs[]`. ALU, load/store, atomic, branch, call, tail-call, and exit opcodes are translated directly. Probe and arena accesses populate exception-table records that let `ex_handler_bpf()` skip faulting instructions and zero destination registers. Exit emits one cleanup epilogue; later exits branch to it.

Trampoline generation separately builds a stack frame around traced kernel calls. It saves arguments into a synthetic context, optionally calls fentry/fmod_ret/fexit programs, invokes the original function when requested, restores registers/return values, and emits a return or frame skip. Dispatcher generation sorts function addresses and emits a recursive binary-search tree of compares and direct/indirect jumps.

## State and persistence
Persistent mutable state is mostly stored in `struct bpf_prog` and `prog->aux`: `bpf_func`, `jited`, `jited_len`, `extable`, `poke_tab`, `priv_stack_ptr`, `jit_data`, kallsyms metadata, and instruction pointer arrays. During compilation, `addrs[]`, `ctx`, image pointers, and old program length are pass state. Direct tail-call patch descriptors persist target, bypass, and adjustment addresses for later map updates. Private stacks are per-CPU allocations with guard words checked during free. Text mutation is serialized with `text_mutex`, and runtime tail-call target replacement uses RCU synchronization on removal paths.

## Dependencies and integration points
The file depends on Linux BPF core structures (`struct bpf_prog`, verifier metadata, BPF maps, trampoline links), x86 code patching (`text_poke_*`, `smp_text_poke_single`, `bpf_jit_binary_pack_*`), CFI/IBT helpers, retpoline/call-depth mitigation helpers, ORC unwind support, exception tables, BTF function models, kfunc metadata, per-CPU allocation, and PCI-unrelated generic kernel memory APIs. It exposes architecture hooks consumed by the BPF core and by tracing/trampoline infrastructure.

## Risks and edge cases
Critical risks are incorrect instruction length accounting, non-converging branch-size decisions, out-of-range call/jump offsets, wrong exception-table metadata, incorrect callee-saved register tracking, unsafe text patch state transitions, and stale tail-call patch descriptors. Arena and probe-memory paths are sensitive because faults must skip only the faulting x86 instruction and must clear the right destination register. Private stack guard failures indicate overflow/underflow after JIT execution. Trampoline code is ABI-sensitive, especially for stack arguments, CFI/FineIBT prefixes, call-depth accounting, fmod_ret branch patching, original-call frame skipping, and tail-call context propagation.

## Test signals
Useful validation includes BPF selftests for JITed ALU/branch/load/store/atomic behavior, tail calls, subprogram tail calls, kfunc calls, arena access, probe memory fault recovery, trampolines/fentry/fexit/fmod_ret, dispatcher behavior, private stack execution, timed may-goto support, and CFI/IBT kernel configurations. Kernel logs containing `bpf_jit: fatal`, `cond_jmp gen bug`, `extable is not populated`, `Target call ... out of range`, or private stack guard errors are strong failure signals. Comparing interpreter and JIT results plus enabling `bpf_jit_enable > 1` dumps helps diagnose emitted instruction mismatches.
