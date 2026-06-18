# sources/distributed-fs/ceph-client/arch/nios2/Kconfig

Purpose: Nios II architecture Kconfig root.

Important APIs/types/functions: root `NIOS2` symbol selects core architecture capabilities; options for checksum/hweight/calibrate delay, FPU disabled, MMU, alignment trap, command line handling, boot link offset, and advanced virtual-region bases.

Control flow and state: configuration drives compiler flags, boot arguments, memory map constants, and platform Kconfig inclusion.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: advanced region bases and command-line precedence can easily produce nonbooting kernels; alignment trap has performance cost.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.
