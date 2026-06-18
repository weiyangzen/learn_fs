# sources/distributed-fs/ceph-client/arch/arm64/include/asm/static_call.h
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/static_call.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/static_call.h` Defines arm64 static-call trampolines as executable stubs that branch through a rodata target pointer. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
__ARCH_DEFINE_STATIC_CALL_TRAMP(), ARCH_DEFINE_STATIC_CALL_TRAMP(), ARCH_DEFINE_STATIC_CALL_NULL_TRAMP(), ARCH_DEFINE_STATIC_CALL_RET0_TRAMP(). The file is 31 lines / 1050 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
The macro emits a BTI-compatible function in .static_call.text that adrp/ldr loads a nearby rodata quad and br x16 to the target.

### State, Persistence, And Dependencies
Persistent state is generated text and rodata target pointer patched/managed by static call core. Integrates with linux static_call infrastructure, BTI, text patching, and return0 fallback.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Instruction sequence, alignment, symbol sizing, and BTI hint must be valid for alternatives/static-call patching; rodata indirection must remain reachable.

### Test Signals
Build static_call users, objdump trampolines, run static_call selftests, and BTI-enabled boot tests.
