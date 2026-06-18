<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/efi/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/platform/efi/Makefile

## Purpose
This Makefile selects x86 EFI support objects and disables sanitizing/profiling options that are unsafe or undesirable for early/runtime firmware call paths.

## Important APIs, types, and functions
It sets `KASAN_SANITIZE := n` and `GCOV_PROFILE := n`. `CONFIG_EFI` builds `memmap.o`, `quirks.o`, `efi.o`, architecture-width `efi_$(BITS).o`, and `efi_stub_$(BITS).o`. `CONFIG_EFI_MIXED` adds `efi_thunk_$(BITS).o`; `CONFIG_EFI_RUNTIME_MAP` adds `runtime-map.o`.

## Control flow
No runtime control flow. Kbuild compiles width-specific C and assembly support according to kernel bitness and EFI feature config.

## State and persistence behavior
No runtime state. Build output controls availability of EFI memory map handling, runtime services, mixed-mode thunks, and runtime map exposure.

## Dependencies and integration points
It integrates with x86 platform Kbuild, EFI Kconfig, bitness-specific object naming, KASAN, and GCOV. The sanitizer/profiling disables matter for firmware ABI stubs and early boot mappings.

## Risks and edge cases
Sanitizer instrumentation in EFI runtime call paths could break firmware ABI assumptions or early address-space transitions. Missing mixed-mode thunk objects would break 64-bit kernels booted via 32-bit EFI.

## Test signals
Build 32-bit EFI, 64-bit EFI, mixed-mode EFI, and EFI runtime-map configs. Confirm expected object files are linked and no KASAN/GCOV instrumentation is applied in this directory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/efi/Makefile -->
