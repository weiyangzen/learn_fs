# sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/coherency_ll.S

Purpose: Low-level MVEBU coherency assembly routines run during early CPU bring-up and low-power transitions.

Important APIs/types/functions: Defines routines such as `ll_add_cpu_to_smp_group`, `ll_enable_coherency`, and related coherency toggles referenced by C code.

Control flow: Assembly accesses coherency fabric registers through global base/physical symbols, sets CPU membership/coherency bits, and returns to C/boot code.

State and persistence: Hardware state is coherency fabric CPU membership and enable bits; software state is implicit via global base symbols.

Dependencies and integration points: Depends on `coherency.c` globals, ARM assembler conventions, and Armada coherency register layout.

Risks: Must be safe in early/physical contexts and preserve required registers. Bad ordering can produce cache/DMA corruption.

Test signals: Boot secondary CPUs, hotplug, suspend/resume if relevant, and DMA stress after coherency enable.
