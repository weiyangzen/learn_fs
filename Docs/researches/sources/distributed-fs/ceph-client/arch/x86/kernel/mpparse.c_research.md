# sources/distributed-fs/ceph-client/arch/x86/kernel/mpparse.c

Purpose: Parses legacy Intel MultiProcessor Specification tables on x86, registers processors, buses, IOAPICs, and interrupt sources, constructs default MP tables when needed, scans BIOS memory for floating pointers, and optionally updates broken MP IRQ entries.

Important APIs/types/functions: public init hooks include `mpparse_find_mptable()`, `mpparse_parse_early_smp_config()`, `mpparse_parse_smp_config()`, `e820__memblock_alloc_reserved_mpc_new()`, and late `update_mp_table()`. Helpers include `smp_scan_config()`, `smp_read_mpc()`, `smp_check_mpc()`, `check_physptr()`, default table constructors, IRQ replacement helpers, and early params `update_mptable` and `alloc_mptable`.

Control flow: early scanning checks the first 1 KB, top of base RAM, BIOS region, and EBDA for a valid MP floating pointer. It reserves MP structures in memblock. Early parse can register the LAPIC address. Full parse validates MPC signature/checksum/version/LAPIC address, processes entries for CPUs, buses, IOAPICs, interrupt sources, and LINT sources, or constructs default ISA/EISA/PCI tables from floating-pointer feature bytes. If IOAPIC IRQ entries are absent it synthesizes defaults. Optional late update rewrites or copies the MP table and replaces level-low PCI interrupt sources with ACPI/PIRQ-discovered entries.

State and persistence: boot-time state includes `num_procs`, `mpf_base`, `mpf_found`, `irq_used`, spare IRQ entry slots, `enable_update_mptable`, and optional allocated replacement MPC physical memory. Parsed data populates global topology, bus, IOAPIC, and `mp_irqs` state.

Dependencies and integration points: depends on BIOS EBDA access, early memremap, memblock reservation, APIC/topology registration, IOAPIC IRQ domains, ACPI coexistence flags, PCI routing, E820 allocation, MTRR/boot CPU data for default CPU entries, and legacy PIC ELCR registers.

Risks: malformed MP tables can disable SMP or fall back to default IRQ routing. ACPI-provided LAPIC/IOAPIC data suppresses some MPS parsing because MPS lacks hyperthreading detail. In-place MP table update can fail on read-only mappings; allocated replacement must be large enough and checksum-fixed. IRQ rewrite has limited spare slots.

Test signals: legacy BIOS or emulator tests should cover valid MP 1.1/1.4 tables, default configurations, missing IRQ entries, bad checksum/signature/version, ACPI coexistence, EBDA-only floating pointer, `update_mptable`, `alloc_mptable=`, PCI routeirq interaction, ELCR fallback, and memblock reservations.
