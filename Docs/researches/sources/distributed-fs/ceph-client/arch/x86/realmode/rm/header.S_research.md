<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rm/header.S -->
# sources/distributed-fs/ceph-client/arch/x86/realmode/rm/header.S

## Purpose
`header.S` defines the read-only real-mode blob header that the protected-mode kernel uses to find trampoline, wakeup, restart, and page-table entry points after relocation.

## Important APIs, types, and functions
It emits `real_mode_header` in `.header` with offsets such as `pa_text_start`, `pa_ro_end`, `pa_trampoline_start`, `pa_trampoline_header`, optional SEV-ES and 64-bit trampoline pointers, ACPI wakeup pointers, `pa_machine_real_restart_asm`, and the 32-bit kernel CS value. It also emits `end_signature`.

## Control flow
The linker resolves `pa_*` symbols from `pasyms.h`; `init.c` copies the blob and patches this header before consumers dereference it. The `.signature` value lets wakeup code verify the complete real-mode region.

## State and persistence behavior
State is intentionally read-only header metadata. Mutable state must live in `.data`/`.bss` through pointers so page permissions can protect the header.

## Dependencies and integration points
It depends on `realmode.h`, linker-script symbols, `CONFIG_AMD_MEM_ENCRYPT`, `CONFIG_X86_64`, and `CONFIG_ACPI_SLEEP` layout choices.

## Risks and edge cases
The C `struct real_mode_header` must match field order exactly. Missing or reordered fields will redirect CPU startup or restart code to the wrong physical offset.

## Test signals
Test signals are compile-time structure layout agreement, valid `REALMODE_END_SIGNATURE`, successful relocation, and boot/resume paths that consume every configured header pointer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rm/header.S -->
