# sources/distributed-fs/ceph-client/arch/mips/sibyte/sb1250/time.c

Purpose: minimal SB1250 time initialization.

Important APIs/types/functions: `plat_time_init` sets `mips_hpt_frequency`.

Control flow and state: boot-time hook derives the MIPS high-precision timer frequency from `zbbus_mhz * 500000`.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: incorrect ZBbus frequency produces wrong scheduler clock/timer calibration.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.
