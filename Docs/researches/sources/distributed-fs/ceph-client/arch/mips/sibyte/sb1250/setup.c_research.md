# sources/distributed-fs/ceph-client/arch/mips/sibyte/sb1250/setup.c

Purpose: detects SB1250/BCM112x SoC type, revision, workaround level, bus clock, and platform setup details.

Important APIs/types/functions: `setup_bcm1250`, `setup_bcm112x`, `sys_rev_decode`, `sb1250_setup`, exported `soc_type`, `periph_rev`, `zbbus_mhz`, and `sb1250_m3_workaround_needed`.

Control flow and state: early setup reads SCD system revision, decodes pass strings and peripheral revisions, selects workaround pass flags, reports unsupported errata/config combinations, derives ZBbus MHz, and installs machine restart/halt/poweroff behavior through platform hooks.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: revision decoding must match silicon exactly; compile-time errata options can be unsafe for old passes; bus-frequency detection affects timers/profiling; boot can intentionally panic if required SB1 workarounds are absent.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.
