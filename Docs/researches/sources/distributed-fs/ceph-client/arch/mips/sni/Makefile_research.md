# sources/distributed-fs/ceph-client/arch/mips/sni/Makefile

Purpose: Kbuild list for SNI RM platform support.

Important APIs/types/functions: `obj-y` adds IRQ, reset, setup, A20R, RM200, PCIMT, PCIT, time; `CONFIG_EISA` adds `eisa.o`.

Control flow and state: platform build always includes all SNI board variants and dispatches at runtime by `sni_brd_type`.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: build coverage must include optional EISA to catch root-device integration.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.
