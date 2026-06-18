# sources/distributed-fs/ceph-client/arch/mips/sni/setup.c

Purpose: SNI platform setup and board detection from firmware/IDPROM.

Important APIs/types/functions: `sni_display_setup`, `sni_console_setup`, `sni_idprom_dump`, `plat_mem_setup`, Cirrus PCI RAM-size quirk, and machine hook assignment.

Control flow and state: boot reads firmware data, sets console/screen information, determines `sni_brd_type`, establishes memory/resource ranges, installs restart/power hooks, and applies PCI quirks for onboard graphics.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: firmware environment and IDPROM parsing are early-boot fragile; console fallback affects diagnostics; PCI quirk must target only affected Cirrus devices.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.
