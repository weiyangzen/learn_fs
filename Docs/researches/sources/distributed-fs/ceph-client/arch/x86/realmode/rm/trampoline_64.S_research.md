<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rm/trampoline_64.S -->
# sources/distributed-fs/ceph-client/arch/x86/realmode/rm/trampoline_64.S

## Purpose
`trampoline_64.S` implements the 64-bit AP trampoline for real-mode, SEV-ES, compatibility-mode, and direct 64-bit BIOS entry paths.

## Important APIs, types, and functions
Important symbols are `trampoline_start`, optional `sev_es_trampoline_start`, `startup_32`, `pa_trampoline_compat`, `startup_64`, `trampoline_start64`, descriptor tables `tr_gdt`/`tr_gdt64`/`tr_compat`, `trampoline_pgd`, and `trampoline_header` fields for start, EFER, CR4, flags, and lock.

## Control flow
The real-mode path serializes stack use, optionally verifies long-mode support, loads IDT/GDT, enters protected mode, handles SME MSR setup, installs CR4/CR3/EFER, enables paging/long mode, and jumps to 64-bit kernel entry. The direct 64-bit path checks LA57 paging compatibility and either jumps directly with trampoline PGD or drops through compatibility mode to switch paging width.

## State and persistence behavior
Persistent blob state includes the trampoline page table, duplicated GDTs, lock word, CR4/EFER/start fields, and SME flag. CPU state transitions cover CR0, CR3, CR4, EFER, segment registers, and stack.

## Dependencies and integration points
It depends on `verify_cpu.S`, AMD memory-encryption flags, `struct trampoline_header`, `init.c` header initialization, and page-table constants for 4-level/5-level switching.

## Risks and edge cases
Relocation avoidance is critical; the comment explicitly requires objdump relocation checks. Races on the shared real-mode stack are controlled by `tr_lock`. EFER writes are skipped when already correct to avoid TDX #VE behavior.

## Test signals
Signals include 64-bit SMP and CPU hotplug, SEV-ES AP startup, SME-enabled boot, LA57 paging transitions, direct 64-bit firmware handoff testing, and relocation-free objdump validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rm/trampoline_64.S -->
