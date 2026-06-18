# sources/distributed-fs/ceph-client/arch/nios2/boot/compressed/misc.c

Purpose: Nios II gzip decompressor C support.

Important APIs/types/functions: `memset`, `memcpy`, `fill_inbuf`, `flush_window`, `error`, `decompress_kernel`, included inflate implementation.

Control flow and state: sets input/output buffers from linker symbols and configured memory base, inflates kernel data, optionally prints progress/errors, and returns to assembly jump path.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: minimal libc replacements must be correct; output address must not overlap decompressor/piggy data incorrectly.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.
