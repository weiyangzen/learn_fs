<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-iproc-asiu.c -->
# sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-iproc-asiu.c

Purpose: This shared helper implements iProc ASIU gate and divider clocks, registering a onecell provider from SoC-specific divider/gate descriptor arrays.

Important APIs, types, and functions: `iproc_asiu_clk` stores a `clk_hw`, name, parent ASIU object, cached rate, and per-clock `iproc_asiu_div`/`iproc_asiu_gate` descriptors. `iproc_asiu` stores divider/gate MMIO bases, onecell data, and the clock array. Clock ops are `iproc_asiu_clk_enable()`, `iproc_asiu_clk_disable()`, `iproc_asiu_clk_recalc_rate()`, `iproc_asiu_clk_determine_rate()`, and `iproc_asiu_clk_set_rate()`. Public setup is `iproc_asiu_setup()`.

Control flow: Setup validates descriptor pointers, allocates onecell data and clock storage, maps divider and gate resources, then loops over `clock-output-names`, registering one clock per descriptor with a common parent. Enable/disable toggles gate bits unless the descriptor marks the gate offset invalid. Recalc reads the divider enable bit and high/low divider fields; if disabled, the clock follows the parent rate. Set-rate either disables the divider for parent rate or computes a rounded divider and writes high/low fields.

State and persistence behavior: Hardware state is split between divider and gate register spaces. The driver has no locking around read-modify-write sequences, so it relies on early/static setup and limited concurrent mutation. Software state persists in allocated arrays referenced by registered clocks.

Dependencies and integration points: It depends on `clk-iproc.h` descriptor definitions, common clock framework, OF `clock-output-names`, one parent clock, and SoC descriptor files such as `clk-cygnus.c`.

Risks and test signals: Risks include no register lock, odd-divider rounding because both high and low fields are derived from `div >> 1`, invalid gate offsets for always-on clocks, and cleanup correctness on partial registration. Tests should verify enable/disable bits, exact and rounded rates, parent-rate passthrough, ASIU clock-output-name ordering, and cleanup paths under registration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-iproc-asiu.c -->
