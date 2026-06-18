# sources/distributed-fs/ceph-client/arch/x86/mm/cpu_entry_area.c

## Purpose
Builds per-CPU CPU-entry-area mappings used by x86 entry code for GDT, TSS, entry stacks, exception stacks, and debug-store areas.

## Important APIs, Types, And Functions
Exports `get_cpu_entry_area(int cpu)` and `cea_set_pte()`. Initialization is driven by `setup_cpu_entry_areas()`, with helpers `init_cea_offsets()`, `setup_cpu_entry_area_ptes()`, `setup_cpu_entry_area()`, `percpu_setup_exception_stacks()`, and `percpu_setup_debug_store()`.

## Control Flow
On x86-64, KASLR can randomize each CPU's CEA slot; without KASLR the CPU number is used. Setup populates required PTEs, maps read-only GDT/TSS on 64-bit or writable versions on 32-bit, maps per-CPU entry and exception stacks with guard pages, conditionally maps VC stacks for encrypted guests, maps Intel debug-store data, then syncs the initial page table.

## State And Persistence
Creates permanent kernel mappings in the CPU entry area and initializes per-CPU pointers such as `cea_exception_stacks` and `_cea_offset`. Page tables are modified via `set_pte_vaddr()`.

## Dependencies And Integration Points
Entry assembly, traps, double-fault/NMI/MCE/#VC handling, KASAN shadow population, PTI/shared page tables, fixmap, descriptor tables, and per-CPU storage all depend on these mappings.

## Risks
Incorrect mapping protections can fault in entry code or weaken isolation. TSS layout assertions protect CPU errata around page boundaries. KASLR offset selection is O(n^2) and must avoid duplicate CEA slots. CEA PTEs are global only when present to avoid `PROT_NONE` confusion.

## Test Signals
Boot on 32/64-bit, KASLR and non-KASLR, PTI, AMD encrypted guests with #VC, Intel debug-store support, KASAN, CPU hotplug/possible CPU count variants, and fault injection on exception stacks.
