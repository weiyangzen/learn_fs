# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-debugfs.c

## Purpose

`xgbe-debugfs.c` exposes low-level debugging controls for AMD XGBE hardware registers. It creates one debugfs directory per netdev and provides register selector/value pairs for XGMAC MMIO, XPCS MDIO/MMD access, optional MAC property registers, optional I2C control registers, and optional auto-negotiation CDR workaround booleans.

This is a diagnostic surface rather than a data-path component. It gives privileged users raw read/write access to selected register spaces using the same register helper macros as the driver.

## Important APIs and Functions

- `xgbe_common_read()` formats a 32-bit value as `0x%08x\n` and uses `simple_read_from_buffer`.
- `xgbe_common_write()` accepts one hexadecimal integer at offset zero and stores it in a caller-provided `unsigned int`.
- XGMAC files: `xgmac_register` selects `pdata->debugfs_xgmac_reg`; `xgmac_register_value` reads/writes `XGMAC_IOREAD/IOWRITE` at that offset.
- XPCS files: `xpcs_mmd`, `xpcs_register`, and `xpcs_register_value` select an MMD/register pair and read/write through `XMDIO_READ/WRITE`.
- Optional XPROP files: `xprop_register` and `xprop_register_value` use `XP_IOREAD/IOWRITE` when `pdata->xprop_regs` exists.
- Optional XI2C files: `xi2c_register` and `xi2c_register_value` use `XI2C_IOREAD/IOWRITE` when `pdata->xi2c_regs` exists.
- Optional booleans: `an_cdr_workaround` and `an_cdr_track_early` expose runtime workaround flags if the variant data enables the CDR workaround.
- `xgbe_debugfs_init()`, `xgbe_debugfs_exit()`, and `xgbe_debugfs_rename()` manage the debugfs directory lifecycle.

## Control Flow

Initialization sets default selector values, creates a directory named `amd-xgbe-%s`, then creates register selector and value files with mode `0600`. A read of a selector file returns the cached selector. A write to a selector file updates the cached offset or MMD. A read of a value file performs the current hardware access and returns the result. A write to a value file parses a hex value and writes it to the selected register.

Directory teardown is a single recursive debugfs removal. Rename updates the directory name after netdev rename using `debugfs_change_name`.

## State and Persistence Behavior

Persistent state is limited to selector fields in `struct xgbe_prv_data`: `debugfs_xgmac_reg`, `debugfs_xpcs_mmd`, `debugfs_xpcs_reg`, `debugfs_xprop_reg`, and `debugfs_xi2c_reg`, plus the workaround booleans. These are runtime-only and reset on device reprobe or driver unload. Hardware writes performed through debugfs mutate live device state and can survive until reset or later driver reconfiguration.

## Dependencies and Integration Points

The file depends on Linux debugfs, module ownership, simple read/write helpers, slab allocation, and xgbe register macros from `xgbe-common.h`. It integrates with the probe/remove/rename lifecycle through calls from the broader driver. XPCS value access goes through `pdata->hw_if.read_mmd_regs`/`write_mmd_regs`, so it shares locking and platform-specific access semantics from `xgbe-dev.c`.

## Risks and Failure Modes

- There is no range validation for register offsets. A privileged writer can select offsets outside the intended documented register range for a mapped block.
- Register value writes can disrupt a live data path, link training, I2C transactions, timestamping, or interrupt behavior.
- The selector/value sequence is not atomic across users. Concurrent debugfs users can change a selector between another user's selector write and value read/write.
- `xgbe_common_write()` treats parse failures as `-EIO`; scripts may need to distinguish invalid input from hardware failures separately.
- `xgbe_debugfs_init()` does not check each `debugfs_create_file()` result, which is typical for debugfs but means missing entries may only be noticed by inspection.

## Test Signals

Mount debugfs and verify directory creation, rename after netdev rename, and cleanup on device removal. Read XGMAC feature or version registers through the selector/value pair and compare with driver logs. Exercise XPCS reads against known MMD registers. Negative tests should include too-small read buffers, nonzero write offsets, overlong writes, invalid hex input, and concurrent selector changes. Avoid destructive value writes except on disposable hardware or with a documented register plan.
