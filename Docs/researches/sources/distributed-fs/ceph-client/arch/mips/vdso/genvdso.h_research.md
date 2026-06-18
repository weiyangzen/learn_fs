# sources/distributed-fs/ceph-client/arch/mips/vdso/genvdso.h

Purpose: template header included twice by `genvdso.c` to specialize ELF32 and ELF64 patch/symbol routines.

Important APIs/types/functions: `FUNC(patch_vdso)`, `FUNC(get_symbols)`, section header/string/symbol scanning, ABI flag interpretation.

Control flow and state: compiled with `ELF_BITS` set to 64 then 32; locates special MIPS sections, updates section names/types, determines ABI mask, and finds symbol values for ABI-required vDSO symbols.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: template macro expansion is hard to audit; section/name assumptions must track linker script and `elf.S`; wrong ABI mask omits required symbols.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.
