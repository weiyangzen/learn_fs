# sources/distributed-fs/ceph-client/drivers/firmware/samsung/exynos-acpm-pmic.c

## Purpose
`exynos-acpm-pmic.c` builds ACPM PMIC commands for register read, bulk read, write, bulk write, and masked update operations.

## Important APIs, Types, And Functions
- Bitfield definitions encode channel, PMIC type, register, return code, mask, value, and function ID.
- `enum exynos_acpm_pmic_func` defines read/write/update/bulk command IDs.
- Error mapping: `acpm_pmic_linux_errmap[]` and `acpm_pmic_to_linux_err()`.
- Bulk packing helpers: `acpm_pmic_set_bulk()` and `acpm_pmic_get_bulk()`.
- Command initializers for each operation type.
- Exported internal helpers: `acpm_pmic_read_reg()`, `acpm_pmic_bulk_read()`, `acpm_pmic_write_reg()`, `acpm_pmic_bulk_write()`, and `acpm_pmic_update_reg()`.

## Control Flow
Each operation fills a four-word command with PMIC address fields and function code, uses `acpm_pmic_set_xfer()` to make the command both TX and RX, calls `acpm_do_xfer()`, and maps the firmware return field to Linux errno. Reads extract the value field; bulk reads unpack up to eight bytes from response words 2 and 3; bulk writes pack up to eight bytes into command words 2 and 3.

## State And Persistence
The file stores no state. PMIC writes and updates persist in hardware/firmware PMIC state until changed again. Command buffers are stack-local and synchronous.

## Dependencies And Integration Points
It depends on the core ACPM transfer API, bitfield helpers, timekeeping for timestamps on some commands, and the public ACPM protocol handle. `exynos-acpm.c` installs these helpers into `pmic_ops`.

## Risks
Bulk count is capped at eight bytes; larger requests return `-EINVAL`. Firmware return codes outside the known map become `-EIO`. Command fields are compact and firmware-specific, so bitfield mistakes can target wrong channels/registers. Some bulk command initializers do not set timestamps, so compatibility depends on firmware not requiring them for those functions.

## Test Signals
PMIC clients should read/write single registers, bulk transfer up to eight bytes, and perform masked updates with expected hardware effects. Firmware access errors should map to `-EACCES`; unknown firmware status should become `-EIO`.
