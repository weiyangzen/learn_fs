# sources/distributed-fs/ceph-client/arch/arm64/include/asm/scs.h
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/scs.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/scs.h` Defines Shadow Call Stack assembly macros and dynamic SCS patching support for arm64. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
Assembler macros scs_load_current_base, scs_load_current, scs_save; dynamic_scs_init(); EDYNSCS_* error codes; __pi_scs_patch(). The file is 68 lines / 1276 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
Assembly entry/switch paths load or save x18 SCS pointer from task thread_info when CONFIG_SHADOW_CALL_STACK is enabled. Dynamic SCS can enable a static branch after early patching reports support.

### State, Persistence, And Dependencies
Persistent state is per-task scs_base/scs_sp and dynamic_scs_enabled static branch. Patch state lives in transformed unwind/frame data. Depends on asm-offsets, sysreg, linux/scs, cpufeature; integrates with entry code, context switch, compiler SCS instrumentation, and PAC-to-SCS patching.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
x18 is ABI-reserved for SCS; wrong offsets or save/load omissions break returns. Dynamic patching errors can corrupt EH frame metadata.

### Test Signals
Run SCS-enabled boot, context-switch, stack unwinding, dynamic SCS patch dry-run/error tests, and compiler instrumentation coverage.
