# sources/distributed-fs/ceph-client/drivers/memory/pl353-smc.c

## Purpose
`pl353-smc.c` is the ARM PL353 static memory controller wrapper used by Xilinx platforms. It enables required clocks, instantiates one supported child device, and handles clock gating for suspend/resume.

## Important APIs, Types, And Functions
`struct pl353_smc_data` stores `memclk` and `aclk`. `pl353_smc_probe()` obtains enabled `apb_pclk` and `memclk`, stores drvdata, scans available child nodes, accepts `cfi-flash` or `arm,pl353-nand-r2p1`, creates the first matching child platform device, and fails if none match. PM callbacks disable clocks on suspend and re-enable `aclk` then `memclk` on resume with rollback if memory clock enable fails.

## Control Flow
AMBA probe allocates state and enables clocks through devm clock helpers. It loops over children with scoped OF iteration, warns for unsupported children, creates the first supported child, and breaks. Suspend/resume only handles clock state; no SMC register programming is performed here.

## State And Persistence
Runtime state is clock pointers. Hardware register state is not saved/restored by this file. Child devices own their own flash/NAND state.

## Dependencies And Integration Points
The driver integrates with AMBA matching ID `0x00041353`, OF child nodes, clock framework, platform child creation, and simple dev PM ops. It is a parent for CFI flash and PL353 NAND children.

## Risks
Only a single child is supported; additional valid children are ignored after the first match. No child depopulation is implemented in remove because there is no remove callback. Resume depends on clock enable ordering and rolls back only `aclk` if `memclk` fails.

## Test Signals
Tests should verify probe with flash and NAND child nodes, failure with no supported children, warning for unsupported children, clock enable/disable balance, and resume failure rollback when `memclk` cannot be enabled.
