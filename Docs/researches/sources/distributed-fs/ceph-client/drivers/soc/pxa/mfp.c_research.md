# sources/distributed-fs/ceph-client/drivers/soc/pxa/mfp.c

## Purpose
Implements legacy PXA/MMP Multi-Function Pin register programming for run mode and low-power mode.

## Important APIs, Types, And Functions
Exports in-file functions used by platform code: `mfp_config()`, `mfp_read()`, `mfp_write()`, `mfp_init_base()`, `mfp_init_addr()`, `mfp_config_lpm()`, and `mfp_config_run()`. Main state is `struct mfp_pin` and the global `mfp_table[MFP_PIN_MAX]`. Register encodings are derived from `linux/soc/pxa/mfp.h` macros.

## Control Flow
Early platform setup calls `mfp_init_base()` to store the MFPR MMIO base and mark all pins unconfigured, then `mfp_init_addr()` to fill per-pin register offsets from address maps. `mfp_config()` decodes each packed pin config into alternate function, drive strength, low-power state, edge wake settings, and pull mode. It computes separate run and low-power register values when explicit pull mode conflicts with low-power bits, writes run-mode values immediately, and does a readback sync. `mfp_config_lpm()` and `mfp_config_run()` iterate configured pins and write saved low-power or run values.

## State And Persistence
State is global and hardware-facing: `mfpr_mmio_base`, `mfpr_off_readback`, and per-pin cached config/run/lpm values. Hardware MFPR registers retain the active mode until changed or reset.

## Dependencies And Integration Points
Depends on PXA MFP packed config definitions, raw MMIO access, init-time platform address maps, and suspend/resume or PM code that calls low-power/run reconfiguration.

## Risks
The code uses `BUG_ON()` for invalid pins, which turns bad platform data into a fatal failure. Raw accessors and global state assume single initialized MMIO base. `mfp_config_lpm()` and `mfp_config_run()` iterate without taking `mfp_spin_lock`, relying on external serialization during power transitions. Wake edge clearing order in `__mfp_config_lpm()` is important to avoid stale edge status.

## Test Signals
Platform boot should show correct pin functions and drive states. Suspend/resume testing should verify low-power pin levels, wake edges, and run-mode restoration. Invalid address maps or pin IDs should be caught during board bring-up.
