# sources/distributed-fs/ceph-client/drivers/pinctrl/sprd/pinctrl-sprd.h

## Purpose
This header defines the packed metadata contract between Spreadtrum SoC pin tables and the common Spreadtrum pinctrl core. It also declares the exported lifecycle helpers used by SoC-specific platform drivers.

## Important APIs, types, and functions
`SPRD_PIN_INFO()` packs pin number, pin type, global-control bit offset, bit width, and global-control register index into one integer. `SPRD_PINCTRL_PIN()` and `SPRD_PINCTRL_PIN_DATA()` unpack that value into `struct sprd_pins_info`. `enum pin_type` classifies entries as `GLOBAL_CTRL_PIN`, `COMMON_PIN`, or `MISC_PIN`. `struct sprd_pins_info` is the SoC table element consumed by `sprd_pinctrl_core_probe()`. The exported functions are `sprd_pinctrl_core_probe()`, `sprd_pinctrl_remove()`, and `sprd_pinctrl_shutdown()`.

## Control flow
SoC files define enum constants with `SPRD_PIN_INFO()` and then instantiate a `sprd_pins_info[]` table using `SPRD_PINCTRL_PIN()`. The common core reads the unpacked fields and computes register addresses differently for global-control versus common/misc pins. The header itself has no runtime control flow.

## State and persistence behavior
There is no runtime state in this header. Its bitfield layout is persistent ABI within this driver family: changing offsets, masks, or type values would change how all Spreadtrum SoC tables decode.

## Dependencies and integration points
The header forward-declares `struct platform_device` and is included by both the common core and SC9860 wrapper. It integrates with Linux module symbol exports indirectly by declaring the common functions.

## Risks
The packed format allocates 12 bits for pin number, 4 bits for type, 8 bits for bit offset, 4 bits for width, and 4 bits for register index. Larger future register indices or widths would be truncated. The macro uses token stringification for pin names, so renaming enum tokens changes the DT-visible name expected by the common parser. Because common/misc register offsets are inferred from array order, the header's compact representation does not encode enough information to protect against table-order mistakes.

## Test signals
Compile tests for all Spreadtrum SoC tables validate macro expansion. A useful review check is to decode a few enum entries manually and confirm `.num`, `.type`, `.bit_offset`, `.bit_width`, and `.reg` match hardware documentation. DT parsing tests should use the stringified names emitted by `SPRD_PINCTRL_PIN()`.
