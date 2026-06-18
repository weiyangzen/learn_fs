# sources/distributed-fs/ceph-client/arch/mips/sibyte/swarm/rtc_xicor1241.c

Purpose: direct SMBus access helpers for Xicor X1241 RTC persistent clock.

Important APIs/types/functions: `xicor_read`, `xicor_write`, `xicor_set_time`, `xicor_get_time`, `xicor_probe` and X1241 CCR/SRAM register constants.

Control flow and state: helpers issue two-byte register-address SMBus transactions, convert BCD date/time values, handle status bits, and expose probe/get/set hooks used by board setup.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: same raw SMBus timeout/locking risks as M41T81; device selection and BCD conversions are board-specific; bad probe can select the wrong RTC implementation.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.
