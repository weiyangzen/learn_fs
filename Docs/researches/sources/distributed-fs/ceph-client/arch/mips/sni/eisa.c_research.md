# sources/distributed-fs/ceph-client/arch/mips/sni/eisa.c

Purpose: virtual EISA root for SNI systems lacking a discoverable bridge.

Important APIs/types/functions: `eisa_root_dev`, `eisa_bus_root`, `sni_eisa_root_init`.

Control flow and state: registers a platform `eisa` device, attaches root data, and calls `eisa_root_register`; if a real bridge exists, it unregisters quietly.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: the return check appears suspicious because it returns immediately on successful platform-device registration before setting drvdata/registering EISA root; root probing depends on call ordering with real bridges.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.
