<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rm/trampoline_32.S -->
# sources/distributed-fs/ceph-client/arch/x86/realmode/rm/trampoline_32.S

## Purpose
`trampoline_32.S` is the 32-bit SMP secondary CPU real-mode trampoline that switches an AP from real mode to protected mode and jumps to `startup_32_smp`.

## Important APIs, types, and functions
Exports include `trampoline_start`, `startup_32`, and `trampoline_header` fields `tr_start`, `tr_gdt_pad`, and `tr_gdt`.

## Control flow
An AP enters in real mode, flushes cache, far-jumps to the relocated segment, initializes DS, disables interrupts, loads the destination from `tr_start`, loads a null IDT and supplied GDT, sets CR0.PE with `lmsw`, and far-jumps to `pa_startup_32`. The 32-bit stub then jumps through EAX.

## State and persistence behavior
State is the trampoline header filled by `init.c` with start address and GDT descriptor. The code otherwise relies on CPU control registers and segment state.

## Dependencies and integration points
It depends on real-mode relocation symbols, `__BOOT_CS`, `startup_32_smp`, and `trampoline_common.S` for IDT storage.

## Risks and edge cases
Bad GDT descriptor placement or a wrong `tr_start` will hang AP bring-up. The code assumes no usable incoming stack and must remain relocation-safe.

## Test signals
Signals are 32-bit SMP boot, CPU hotplug, objdump relocation checks, and AP startup timeout diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rm/trampoline_32.S -->
