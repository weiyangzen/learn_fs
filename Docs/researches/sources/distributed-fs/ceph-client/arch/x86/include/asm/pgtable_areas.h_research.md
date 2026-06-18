# sources/distributed-fs/ceph-client/arch/x86/include/asm/pgtable_areas.h

Purpose: defines architecture-neutral x86 CPU entry area address constants, adding 32-bit-specific area definitions when needed.

Important APIs, types, and functions: includes `pgtable_32_areas.h` for 32-bit builds, then defines `CPU_ENTRY_AREA_RO_IDT`, `CPU_ENTRY_AREA_PER_CPU`, `CPU_ENTRY_AREA_RO_IDT_VADDR`, and `CPU_ENTRY_AREA_MAP_SIZE`.

Control flow: no executable code. `CPU_ENTRY_AREA_MAP_SIZE` is derived differently for 32-bit and 64-bit: precise per-CPU map span on 32-bit and a full `P4D_SIZE` on 64-bit.

State and persistence: no state is owned; these constants describe reserved virtual layout.

Dependencies and integration points: consumed by entry-area setup, IDT mapping, per-CPU entry stacks, fixmap/page-table initialization, and debug page-table validation.

Risks: CPU entry area layout is used by entry/exception code and must remain page-aligned and isolated from adjacent regions. 32-bit and 64-bit map-size assumptions differ significantly.

Test signals: boot on SMP, IDT read-only mapping tests, CPU hotplug entry area setup, page-table dumps of CPU entry area, and exception/interrupt delivery through per-CPU entry structures.
