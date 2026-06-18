# sources/distributed-fs/ceph-client/arch/mips/sibyte/sb1250/Makefile

Purpose: Kbuild list for SB1250 board support.

Important APIs/types/functions: `obj-y := setup.o irq.o time.o`; conditional `smp.o` for `CONFIG_SMP`.

Control flow and state: Kbuild includes setup, interrupt, and time support unconditionally for this platform and adds SMP mailbox/boot support when enabled.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: missing or stale object selection breaks platform boot; dependency is only Kconfig-driven build coverage.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.
