# sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_hal.h

## Purpose
This header defines the host/firmware HAL constants, bootloader command values, firmware-load addresses, watchdog/reset registers, descriptor layouts, and HAL API prototypes shared by USB, SDIO, management, and core code.

## Important APIs, Types, and Functions
Important macro groups include `DEV_OPMODE_*` and `DEV_OPMODE_PARAM_DESC`, flash geometry, ping/pong firmware-load buffers, bootloader command/status bytes, ULP and 9116 watchdog registers, RF SPI/GSPI registers, firmware image limits, version offsets, register sizes, firmware alignment, and RAM access masks. Important types are `bl_header`, `ta_metadata`, `bootload_entry`, `bootload_ds`, `rsi_mgmt_desc`, `rsi_data_desc`, and `rsi_bt_desc`. Declared APIs include `rsi_hal_device_init`, `rsi_prepare_mgmt_desc`, `rsi_prepare_data_desc`, `rsi_prepare_beacon`, `rsi_send_pkt_to_bus`, and `rsi_send_bt_pkt`.

## Control Flow
The header has no executable flow. Its constants drive firmware loading, bootloader handshakes, descriptor preparation, queue selection, watchdog reset, register access, and packet transmission in the corresponding `.c` files.

## State and Persistence Behavior
No software state is stored here. The packed descriptor structures become on-bus ABI sent to firmware. Register constants target persistent device state until reset, especially firmware load buffers, bootloader control registers, watchdog timers, RF SPI controls, and memory-access permissions.

## Dependencies and Integration Points
It is included by USB/SDIO bus drivers, management frame builders, the common core, and HAL implementation files. It integrates with firmware file `rs9113_wlan_qspi.rps`, module operating mode parameters, and bus-specific `rsi_host_intf_ops`.

## Risks
This is a hardware/firmware ABI surface. Wrong constants or descriptor packing can break boot, corrupt packet descriptors, or reset the wrong block. `MAX_FLASH_FILE_SIZE` and alignment constants must match firmware images. Register-size mismatches between 9113 and 9116 paths can cause partial writes. Duplicate names such as common HAL card-ready constants must stay synchronized with management/coex definitions.

## Test Signals
Firmware load over SDIO and USB, bootloader ping/pong handshakes, flash size/version reads, descriptor decode by firmware for mgmt/data/BT packets, watchdog reset for 9113 and 9116, and builds across all transport/coex combinations validate this header.
