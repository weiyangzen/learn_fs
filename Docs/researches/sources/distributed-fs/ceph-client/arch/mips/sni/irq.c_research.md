# sources/distributed-fs/ceph-client/arch/mips/sni/irq.c

Purpose: common SNI interrupt entry and board dispatch selection.

Important APIs/types/functions: `sni_hwint`, `plat_irq_dispatch`, `sni_isa_irq_handler`, `arch_init_irq`.

Control flow and state: the global dispatch hook calls the board-specific `sni_hwint`; ISA handler polls i8259 and forwards to `generic_handle_irq`; arch init initializes legacy i8259 and switches on `sni_brd_type` to initialize A20R, PCIT, PCIMT, or RM200 IRQs.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: if board detection fails, `sni_hwint` may be unset; ISA cascade depends on initialized i8259; board cases must stay synchronized with setup detection.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.
