## sources/distributed-fs/ceph-client/arch/mips/ralink/clk.c

### Purpose
This file initializes timer frequency for non-GIC Ralink SoCs by obtaining the CPU clock from the OF clock provider and setting `mips_hpt_frequency`.

### Important APIs, Types, And Functions
`clk_cpu()` maps the global `ralink_soc` enum to a sysc compatible string and clock index. `plat_time_init()` remaps Ralink OF registers, initializes clocks, fetches the CPU clock, logs the rate, sets `mips_hpt_frequency`, releases the clock, and calls `timer_probe()`.

### Control Flow
Timer init runs after SoC identification. It chooses a compatible/index pair, panics on unsupported SoC, initializes OF clocks, finds the provider node, gets the indexed clock, and derives the MIPS counter frequency as CPU clock divided by two.

### State, Persistence, And Dependencies
Persistent state is `mips_hpt_frequency`. Dependencies include `ralink_soc`, `ralink_of_remap()`, OF clock providers in sysc nodes, clock framework, and MIPS timer probing.

### Integration Points
This is used only when `CONFIG_MIPS_GIC` is not selected; MT7621 uses GIC timer code instead.

### Risks
Missing or mismatched clock providers panic early. The compatible/index table must stay aligned with DT bindings and SoC enum values.

### Test Signals
Boot each non-GIC SoC, verify CPU clock log, timer interrupt cadence, and correct sysc clock index selection.
