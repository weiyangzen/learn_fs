# sources/distributed-fs/ceph-client/arch/mips/txx9/generic/setup_tx4927.c

Purpose: TX4927 SoC setup for clocks, reset/watchdog, bus-error handling, timers, serial, MTD, DMA, and unused-module gating.

Important APIs/types/functions: `tx4927_setup`, `tx4927_wdt_init`, `tx4927_time_init`, `tx4927_sio_init`, `tx4927_mtd_init`, `tx4927_dmac_init`, `tx4927_stop_unused_modules`, `tx4927_late_init`.

Control flow and state: reads CC/clock registers, initializes resource windows, installs bus-error handler, computes CPU/GBUS clocks, initializes timers/SIO/flash/DMA, and disables unused modules late.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: clock/reset register decoding must match silicon; stopping modules can break boards that forgot to register users; watchdog restart is destructive by design.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.
