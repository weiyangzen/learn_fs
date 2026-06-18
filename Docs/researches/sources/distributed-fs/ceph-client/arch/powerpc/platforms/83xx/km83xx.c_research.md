# sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/km83xx.c

## Purpose
`km83xx.c` supports Keymile KMETER1 and related 83xx boards, including QUICC Engine par_io setup and MPC8360E QE_ENET10 erratum handling.

## Important APIs, Types, and Functions
`mpc83xx_km_setup_arch()` runs common setup and, when QUICC Engine is enabled, initializes `par_io`, applies OF pin configuration for SPI and UCC nodes, and invokes `quirk_mpc8360e_qe_enet10()` when a `ucc_geth` network node exists. The erratum helper maps `par_io` registers and adjusts UCC delay bits depending on SVR revision. `mpc83xx_km_probe()` matches Keymile compatibles before the normal machine selection.

## Control Flow, State, and Persistence
Hardware state is persisted in par_io delay and pinmux registers. No local C state remains after init.

## Dependencies and Integration Points
It depends on QUICC Engine, OF par_io/spi/ucc nodes, FSL PCI/SOC helpers, IPIC, and common 83xx restart/time setup.

## Risks and Test Signals
Risks include revision-specific erratum bit programming, missing par_io nodes, and broad node-name scans. Test signals are UCC Ethernet RGMII stability, SPI pin function, board matching for both compatibles, PCI setup, and IPIC interrupts.
