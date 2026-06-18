<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/irq.c -->
## sources/distributed-fs/ceph-client/arch/mips/generic/irq.c

**Purpose:** Provides generic helpers to resolve CP0 FDC, performance counter, and compare interrupt numbers.

**Important APIs/types/functions:** `get_c0_fdc_int()`, `get_c0_perfcount_int()`, and `get_c0_compare_int()` choose GIC-provided interrupt lines, VEIC panic placeholders, or MIPS CPU IRQ base offsets.

**Control flow:** Each function first checks `mips_gic_present()`, then VEIC, then configured CP0 interrupt fields, returning `-1` for unavailable optional interrupts.

**State, dependencies, integration:** Uses global CP0 interrupt configuration variables and GIC helper APIs. Called by timer/perf/FDC setup code.

**Risks and test signals:** VEIC paths are unimplemented and panic. Test with GIC, non-GIC CPU IRQ, no optional irq, and VEIC configurations to expose unsupported paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/irq.c -->
