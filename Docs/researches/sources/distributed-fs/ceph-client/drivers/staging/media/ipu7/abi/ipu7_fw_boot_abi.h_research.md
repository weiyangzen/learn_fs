# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/abi/ipu7_fw_boot_abi.h

## Purpose

This header defines the packed firmware boot ABI shared between host driver and GOFO/IPU firmware. It describes logger configuration, boot parameter register IDs, boot config layout, secondary boot config layout, frequency units, and boot-state/error constants.

## Important APIs, Types, and Functions

Key types are `struct ia_gofo_logger_config`, `struct ia_gofo_boot_config`, and `struct ia_gofo_secondary_boot_config`. Enums include `ia_gofo_buttress_reg_id`, `ia_gofo_boot_uc_tile_frequency_units`, and `ia_gofo_boot_state`. Constants define boot-param register offsets, reserved sizes, logger severity and channel bits, critical error values, and `IA_GOFO_FW_BOOT_STATE_IS_CRITICAL()`.

## Control Flow

The header has no executable flow, but `ipu7-boot.c` follows this state machine: write boot config DMA address and UNINIT state, start uC, poll until READY or critical, later write SHUTDOWN_CMD and poll INACTIVE.

## State and Persistence Behavior

The packed structs are DMA-visible boot memory. Firmware writes boot state, queue indices address, and messaging version back through buttress boot parameter registers.

## Dependencies and Integration Points

It includes `ipu7_fw_common_abi.h` and `ipu7_fw_syscom_abi.h`. It is consumed by boot setup, ISYS firmware setup, and buttress diagnostics.

## Risks and Edge Cases

Every packed field is firmware ABI. Incorrect length, version, queue config offset, or reserved size can prevent firmware boot. Critical states in the `0xdead****` range must be treated as terminal.

## Test Signals

Boot tests should observe UNINIT-to-READY transitions, critical state logging, shutdown to INACTIVE, and queue index/message version register publication.
