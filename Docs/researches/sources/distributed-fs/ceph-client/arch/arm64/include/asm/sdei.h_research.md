# sources/distributed-fs/ceph-client/arch/arm64/include/asm/sdei.h
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/sdei.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/sdei.h` Declares arm64 Software Delegated Exception Interface entry, stack, event state, and conduit helpers. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
SDEI_EXIT_HVC/SMC, SDEI_STACK_SIZE, per-CPU active event pointers, sdei_exit_mode, __sdei_asm_handler(), __sdei_asm_entry_trampoline(), __sdei_handler_abort(), __sdei_handler(), do_sdei_event(), sdei_arch_get_entry_point(). The file is 53 lines / 1569 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
Firmware enters the assembly handler or trampoline, minimal state is captured into pt_regs, then __sdei_handler/do_sdei_event invoke the registered event. Abort discards a running context.

### State, Persistence, And Dependencies
Persistent state includes per-CPU active normal/critical events and sdei_exit_mode. Handler context is transient on SDEI stacks. Depends on linkage, preempt, types, virt, pt_regs; integrates with firmware SDEI driver, KPTI trampoline, stacktrace SDEI stack detection, and exception entry.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Wrong conduit entrypoint or stack sizing can corrupt exception handling; abort paths must not resume discarded contexts; KPTI trampoline must be mapped correctly.

### Test Signals
Run SDEI firmware/emulation tests, normal/critical nesting, KPTI enabled boots, stack unwinding across SDEI stacks, and HVC/SMC conduit coverage.
