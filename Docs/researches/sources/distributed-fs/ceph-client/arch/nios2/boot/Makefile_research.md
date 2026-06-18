# sources/distributed-fs/ceph-client/arch/nios2/boot/Makefile

Purpose: Nios II boot image Makefile.

Important APIs/types/functions: `vmlinux.bin`, `vmlinux.gz`, `vmImage`, `zImage`, compressed `vmlinux` rules and U-Boot load/entry addresses from `nm`.

Control flow and state: objcopy creates binary, gzip compresses it, U-Boot wrapper creates `vmImage`, and compressed build links self-extracting `zImage`.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: entry/load address extraction relies on symbol names; compressed and U-Boot targets require tool availability.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.
