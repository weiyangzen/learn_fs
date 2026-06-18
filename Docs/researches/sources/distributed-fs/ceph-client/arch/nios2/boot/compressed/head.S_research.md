# sources/distributed-fs/ceph-client/arch/nios2/boot/compressed/head.S

Purpose: Nios II compressed boot entry assembly.

Important APIs/types/functions: `_start` relocation, cache init/flush, BSS clear, argument save/restore, stack setup, and `decompress_kernel` call.

Control flow and state: starts at linked decompressor image, invalidates/flushes caches, relocates if needed, clears BSS, preserves boot arguments, calls C decompressor, flushes caches again, and jumps to decompressed kernel address.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: wrong cache or relocation constants corrupt boot; register preservation is bootloader ABI-sensitive.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.
