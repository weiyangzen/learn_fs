# sources/distributed-fs/ceph-client/arch/nios2/boot/compressed/vmlinux.lds.S

Purpose: linker script for Nios II compressed boot image.

Important APIs/types/functions: `OUTPUT_FORMAT`, `OUTPUT_ARCH`, `ENTRY(_start)`, text/rodata/data/got/bss layout and image symbols.

Control flow and state: places decompressor at configured boot link offset and emits symbols consumed by head/misc for relocation, BSS, and piggy data.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: link address and section symbols are boot-critical; GOT/data placement must remain compatible with early assembly.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.
