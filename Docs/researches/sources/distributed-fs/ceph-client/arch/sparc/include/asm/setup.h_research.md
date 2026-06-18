# sources/distributed-fs/ceph-client/arch/sparc/include/asm/setup.h

Purpose: SPARC setup hook declarations shared by boot, console, floppy IRQ, device scan, unaligned/FPU load-store emulation, hypervisor console IRQ migration, and break handling.

Important APIs/types/functions: functions/helpers `con_is_present`, `sparc_floppy_request_irq`, `device_scan`, `safe_compute_effective_address`, `start_early_boot`, `handle_ldf_stq`, `handle_ld_nf`, `sunhv_migrate_hvcons_irq`, `sun_do_break`; macros/constants `_SPARC_SETUP_H`.

Control flow: The file is driven by preprocessor gates such as `_SPARC_SETUP_H`, `CONFIG_SPARC32`, `CONFIG_SPARC64`, `CONFIG_SERIAL_SUNHV`; static inline helpers selected by generic kernel call sites. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management paths rather than through standalone functions.

State and persistence behavior: This header owns no state but wires early boot and trap handlers into global setup state, IRQ descriptors, and CPU/hypervisor state.

Dependencies and integration points: Includes/dependencies: `linux/interrupt.h`, `uapi/asm/setup.h`. Integration points include memory-management; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are register/window layout drift, configuration-specific build gaps, ABI compatibility breaks. Test signals: Boot on supported machines, console detection, floppy IRQ registration, unaligned instruction emulation, and break/NMI paths are signals.
