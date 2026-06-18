<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/board-sead3.c -->
## sources/distributed-fs/ceph-client/arch/mips/generic/board-sead3.c

**Purpose:** Supports legacy MIPS SEAD-3 FPGA boards with YAMON boot data and board-specific FDT fixups.

**Important APIs/types/functions:** `sead3_detect()` checks revision register. FDT fixups append command line, memory, remove GIC if absent, and set serial config. `remove_gic()` rewrites interrupt parents/properties for UART, Ethernet, and EHCI when no GIC is present. `sead3_measure_hpt_freq()` calibrates CP0 count using a sampling status bit. `MIPS_MACHINE(sead3)` registers DTB, detect, fixup, and timer hooks.

**Control flow:** Legacy detection selects built-in DTB, fixup validates root compatible and applies YAMON transformations, and time init measures the counter over 100 10 ms transitions.

**State, dependencies, integration:** Uses raw CKSEG1 registers, libfdt, YAMON DT helpers, generic firmware command line, and built-in `__dtb_sead3_begin`.

**Risks and test signals:** Missing expected DT nodes causes fixup failures; timer calibration busy-waits with IRQs disabled. Test GIC-present and no-GIC boards, UART loop rewriting, memory env parsing, and HPT frequency measurement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/board-sead3.c -->
