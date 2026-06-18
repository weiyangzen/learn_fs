# sources/distributed-fs/ceph-client/arch/mips/vdso/vdso.lds.S

Purpose: linker script for MIPS vDSO shared objects.

Important APIs/types/functions: ABI-dependent `OUTPUT_FORMAT`, `OUTPUT_ARCH`, section layout for notes, dynsym/dynstr, text, eh_frame, dynamic, rodata, versioning, and discard rules.

Control flow and state: defines a compact ET_DYN image layout consumed by the Makefile and `genvdso`.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: section names must align with `genvdso` patching and generic vDSO validation; ABI output format preprocessor branches are critical.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.
