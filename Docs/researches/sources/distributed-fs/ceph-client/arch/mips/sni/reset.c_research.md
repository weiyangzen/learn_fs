# sources/distributed-fs/ceph-client/arch/mips/sni/reset.c

Purpose: SNI restart and power-off hooks.

Important APIs/types/functions: `kb_wait`, `sni_machine_restart`, `sni_machine_power_off`.

Control flow and state: restart disables interrupts and repeatedly pulses the keyboard controller reset command; poweroff writes a control byte to `PCIMT_CSWCSM`.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: restart loops forever if reset does not occur; poweroff is PCIMT-specific magic MMIO and may not apply to every SNI variant.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.
