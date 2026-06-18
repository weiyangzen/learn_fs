# sources/distributed-fs/ceph-client/drivers/soc/ti/pruss.h

## Purpose
This private header defines PRUSS CFG register offsets, bit masks, and inline regmap helpers used by `pruss.c`.

## Important APIs, Types, And Functions
It defines `PRUSS_CFG_*` offsets, GPCFG GPI/mux masks, MII RT event enable, SPP XFR-shift bits, and inline helpers `pruss_cfg_read` and `pruss_cfg_update`. The helpers validate the PRUSS pointer and call `regmap_read` or `regmap_update_bits`.

## Control Flow
There is no independent runtime flow. Callers in `pruss.c` use these definitions to implement exported PRUSS configuration APIs.

## State And Persistence
State is not stored here, but the helpers operate on `pruss->cfg_regmap`; writes persist in the hardware CFG register block.

## Dependencies And Integration Points
The header depends on `struct pruss` being defined by included public PRUSS driver headers before use, and on Linux regmap. It is an internal bridge between exported PRUSS APIs and CFG register programming.

## Risks And Test Signals
Risks include offset or mask drift against new PRUSS variants and use with an invalid/uninitialized regmap. Test signals are successful compilation, correct GPMUX/GPI/MII/XFR register changes, and no invalid pointer warnings from helper users.
