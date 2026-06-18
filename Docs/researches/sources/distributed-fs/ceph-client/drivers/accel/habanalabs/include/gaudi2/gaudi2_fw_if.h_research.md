<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/gaudi2_fw_if.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/gaudi2_fw_if.h

## Purpose
Defines Gaudi2 firmware interface constants shared by the host driver and device firmware: firmware image offsets, mailbox layout, status bits, reset-source values, PLL low frequency, GPIO selection, and redundancy/binning context layout.

## Important APIs, Types, And Functions
- `GAUDI2_EVENT_QUEUE_MSIX_IDX` fixes the event queue MSI-X index to 0.
- `UBOOT_FW_OFFSET` and `LINUX_FW_OFFSET` define bootloader and Linux firmware load offsets.
- `GAUDI2_SP_SRAM_BASE_ADDR`, `GAUDI2_MAILBOX_BASE_ADDR`, mailbox size macros, and derived mailbox address/offset macros describe ARM and ARCPID mailbox windows.
- `POWER_MODE_LEVELS` is a frequency/power table macro.
- `enum gaudi2_fw_status` reports PID, ARM Linux, and management firmware readiness.
- `enum gaudi2_rst_src` defines reset-source bits, including cold, manual, PRSTN, software, firmware, FLR, and ECC double-error reset.
- `struct gaudi2_redundancy_ctx` is a packed little-endian firmware ABI for redundant/disabled HBM, EDMA, TPC, VDEC, MME, NIC, router, HMMU/HIF, xbar, and MME PE isolation masks.

## Control Flow
The driver uses these constants during boot, firmware loading, mailbox setup, event queue setup, and reset diagnosis. Firmware writes status bits and redundancy data into agreed memory/register locations; host code interprets those values according to this header.

## State And Persistence Behavior
The header itself stores no state. It defines persistent-for-boot memory offsets in SRAM/DDR and transient mailbox regions. Reset-source bits and redundancy context survive long enough to be consumed by host initialization and recovery flows, but are device/runtime state rather than filesystem persistence.

## Dependencies And Integration Points
Depends on Linux fixed-width and endian types through includers. Integrates with Gaudi2 boot code, CPUCP/firmware command handling, MSI-X event queue registration, watchdog GPIO programming, power management, and hardware binning/redundancy setup.

## Risks And Edge Cases
This is an ABI boundary. Wrong offsets or sizes can corrupt firmware mailboxes or load images into the wrong memory. The `LINUX_FW_OFFSET` comment says `8BM`, likely a typo for `8MB`, so maintainers should rely on the numeric value. Packed little-endian fields must be converted correctly on the host. Any firmware change to redundancy layout requires synchronized driver changes.

## Test Signals
Signals include firmware boot to PID/ARM/MGMT ready states, successful mailbox command exchange, correct MSI-X event queue setup, reset-source reporting after induced resets, and redundancy masks matching firmware-reported hardware configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/gaudi2_fw_if.h -->
