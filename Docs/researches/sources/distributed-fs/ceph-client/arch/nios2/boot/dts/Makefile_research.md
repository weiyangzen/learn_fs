# sources/distributed-fs/ceph-client/arch/nios2/boot/dts/Makefile

Purpose: Nios II device-tree build rules.

Important APIs/types/functions: `dtb-y` from `CONFIG_BUILTIN_DTB_NAME`; optional all-DTB glob for `CONFIG_OF_ALL_DTBS`.

Control flow and state: selects built-in or all available DTBs for the architecture boot build.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: configuration must name an existing DTS; glob behavior can change build size.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.
