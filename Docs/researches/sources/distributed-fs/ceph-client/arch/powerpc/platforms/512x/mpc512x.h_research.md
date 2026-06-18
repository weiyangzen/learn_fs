# sources/distributed-fs/ceph-client/arch/powerpc/platforms/512x/mpc512x.h

## Purpose
`mpc512x.h` declares the common MPC512x platform services shared by board files and drivers.

## Important APIs, Types, and Functions
It exposes `mpc512x_init_early()`, `mpc512x_init_IRQ()`, `mpc512x_setup_arch()`, `mpc512x_init()`, `mpc512x_restart()`, `mpc5121_clk_init()`, `mpc512x_select_psc_compat()`, and `mpc512x_cs_config()`.

## Control Flow, State, and Persistence
The header owns no data but defines call ordering: early reset/DIU preservation, architecture setup, clock/device/FIFO initialization, IRQ setup, and restart support.

## Dependencies and Integration Points
It is consumed by MPC5121 ADS, generic MPC512x, PDM360NG, the clock provider, and shared code. `mpc512x_cs_config()` is exported for LocalPlus Bus clients.

## Risks and Test Signals
Risks are ABI-like: board files rely on these function names and semantics. Build coverage across all MPC512x board configs and boot coverage on MPC5121 and MPC5125-like DTs validate the header contract.
