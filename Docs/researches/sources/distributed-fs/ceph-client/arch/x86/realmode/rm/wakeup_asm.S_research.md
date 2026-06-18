<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rm/wakeup_asm.S -->
# sources/distributed-fs/ceph-client/arch/x86/realmode/rm/wakeup_asm.S

## Purpose
`wakeup_asm.S` is the ACPI S3 wakeup assembly stub that repairs real-mode segment state, calls wakeup C code, and transfers back to protected/long-mode kernel resume.

## Important APIs, types, and functions
It emits the `wakeup_header` data object, `wakeup_start`, `wakeup_gdt`, and a local real-mode IDT. The header labels must match `struct wakeup_header`.

## Control flow
The stub enters with unknown firmware segment state, temporarily enables protected mode to load known descriptors, returns to real mode, sets stack/segments, validates header and blob signatures, calls `main()`, restores MISC_ENABLE and optionally CR3/CR4/EFER on 32-bit, then jumps through `startup_32` or the 64-bit trampoline.

## State and persistence behavior
Persistent state is the wakeup header and descriptor tables. Runtime state includes restored CR/MSR/GDT/IDT values and stack selection from `rm_stack_end`.

## Dependencies and integration points
It depends on `realmode.h`, `wakeup.h`, `stack.S`, `trampoline_32.S`/`trampoline_64.S`, MSR constants, and ACPI suspend code populating the header.

## Risks and edge cases
Firmware can resume with invalid segment descriptors, which this code explicitly repairs. Any mismatch between C header and assembly data layout breaks resume. Bad signature handling intentionally halts.

## Test signals
Signals include ACPI S3 resume on 32-bit and 64-bit, video-restore combinations, MISC_ENABLE/EFER restore coverage, and disassembly of mode-switch sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rm/wakeup_asm.S -->
