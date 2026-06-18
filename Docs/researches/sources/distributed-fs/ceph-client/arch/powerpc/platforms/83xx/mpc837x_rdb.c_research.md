# sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/mpc837x_rdb.c

## Purpose
`mpc837x_rdb.c` registers MPC837x RDB/WLAN boards and configures board-specific USB/SD pinmux.

## Important APIs, Types, and Functions
`mpc837x_rdb_setup_arch()` runs common setup, configures USB through `mpc837x_usb_cfg()`, and calls `mpc837x_rdb_sd_cfg()`. The SD helper maps IMMR and muxes USBB/SPI pins to SD-card function. The compatible list covers MPC8377/8378/8379 RDB and MPC8377 WLAN boards.

## Control Flow, State, and Persistence
No C state persists. IMMR SICRL/SICRH pinmux writes persist in hardware for the boot session.

## Dependencies and Integration Points
It depends on common 83xx setup, MPC837x USB helper, FSL PCI/SOC, IPIC, OF platform population, and board DT compatible matching.

## Risks and Test Signals
Risks include muxing USBB pins away from USB for SD, which is safe only for RDB-style boards, and fixed IMMR mapping assumptions. Test signals are SD-card operation, USB DR behavior, no conflict on WLAN variants, PCI enumeration, and interrupts.
