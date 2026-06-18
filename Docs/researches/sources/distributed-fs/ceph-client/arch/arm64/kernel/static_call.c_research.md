## sources/distributed-fs/ceph-client/arch/arm64/kernel/static_call.c

### Purpose
`static_call.c` provides the ARM64 architecture hook for updating static-call trampolines by patching the literal target used by generated trampoline code.

### Important APIs, Types, And Functions
It exports `arch_static_call_transform(void *site, void *tramp, void *func, bool tail)`. It uses `__static_call_return0`, `aarch64_insn_adrp_get_offset`, `aarch64_insn_decode_immediate`, and `aarch64_insn_write_literal_u64`.

### Control Flow
If the replacement function is null, the hook targets `__static_call_return0`. It decodes the `adrp` plus immediate sequence in the trampoline to find the literal slot, then writes the new 64-bit function pointer into that slot and warns if patching fails.

### State, Persistence, And Dependencies
The persistent state is patched kernel text or literal data associated with static-call trampolines. There is no runtime allocation and no filesystem state.

### Integration Points
The hook is called by the generic static-call framework and depends on ARM64 text patching and the exact trampoline instruction layout emitted elsewhere in the kernel.

### Risks
Any trampoline layout change breaks literal address decoding. Incorrect patching can redirect indirect calls to invalid code. Instruction endianness, alignment, and text-patching serialization must be respected.

### Test Signals
Enable static calls, exercise call-site updates during boot and module/static-key changes, run objdump checks of trampoline layout, and monitor `WARN_ON_ONCE` from patch failures.
