# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/mac.c

## Purpose

`mac.c` implements low-level MAC and firmware bring-up for `rtw88`. It programs channel-related MAC registers, parses chip power sequences, powers the MAC on and off, downloads firmware through either modern DDMA/reserved-page flow or legacy page writes, configures TX/RX FIFO page layout, maps software queues to hardware priority queues, initializes H2C packet queue state, configures RX driver-info reporting, and runs chip-specific MAC init/postinit hooks.

## Important APIs, Types, and Functions

Public APIs include `rtw_set_channel_mac()`, `rtw_pwr_seq_parser()`, `rtw_mac_power_on()`, `rtw_mac_power_off()`, `rtw_write_firmware_page()`, `rtw_download_firmware()`, `rtw_mac_flush_queues()`, `rtw_set_trx_fifo_info()`, `rtw_ddma_to_fw_fifo()`, `rtw_mac_init()`, and `rtw_mac_postinit()`.

Important internal helpers are `rtw_mac_pre_system_cfg()`, `rtw_mac_power_switch()`, system-config variants for modern and legacy WCPU, firmware size validation, WLAN CPU enable/disable, firmware-download register backup/restore, DDMA setup/checksum helpers, modern and legacy firmware download validators, priority queue configuration, TXDMA queue mapping, H2C queue initialization, and RX driver-info configuration.

## Control Flow

Power-on flow starts in `rtw_mac_power_on()`. It runs pre-system bus and pinmux setup, switches power on using the chip's power-on sequence, handles an already-on MAC by power-cycling and retrying, then initializes system registers using legacy or modern WCPU paths. Power-off delegates to `rtw_mac_power_switch(false)`. Power sequence parsing selects an interface mask from the active HCI type and a cut-version mask from `hal.cut_version`, then executes write, polling, delay, and read commands from chip tables.

Modern firmware download first checks the Realtek firmware header sizes, optionally backs up LTE coexistence state, disables the WLAN CPU, backs up and reprograms TX queue/beacon registers for firmware download, resets the platform, copies DMEM/IMEM/optional EMEM sections through TX buffer plus DDMA into firmware memory, verifies checksums, restores registers, marks firmware download ready, re-enables the CPU, restores LTE coexistence state, validates firmware readiness, resets HCI descriptors, clears H2C counters, and sets `RTW_FLAG_FW_RUNNING`. Legacy firmware download enables legacy firmware-download mode, writes 4 KiB pages through `rtw_hci_write_firmware_page()`, validates report bits, restarts the CPU, and then performs the same HCI/H2C flag reset.

MAC init flow is `rtw_mac_init()`: queue mapping, priority/FIFO page setup, H2C queue setup, chip-specific `mac_init`, RX driver-info configuration, and bus interface config. `rtw_mac_postinit()` calls the optional chip postinit hook. Queue flushing maps mac80211 AC queues through `rtwdev->fifo.rqpn` to hardware priority queues, then polls reserved and available page counts for up to about 100 ms per priority.

## State and Persistence

Persistent driver state updated here includes `RTW_FLAG_POWERON`, `RTW_FLAG_FW_RUNNING`, `rtwdev->fifo` page counts and reserved addresses, `rtwdev->fifo.rqpn`, `rtwdev->h2c.last_box_num`, `rtwdev->h2c.seq`, and MAC/RX configuration registers. Firmware download temporarily backs up six registers and restores them after transfer. Queue setup persists page boundaries, queue maps, H2C queue base/tail pointers, RX FIFO boundaries, and LLT initialization in hardware.

## Dependencies and Integration Points

`mac.c` depends on chip tables and callbacks in `struct rtw_chip_info`, HCI operations for register access and firmware-page writes, firmware reserved-page writer from `fw.c`, SDIO helpers, LTE coexistence accessors, register definitions, and generic helpers such as `check_hw_ready()` and `rtw_restore_reg()`. Higher-level core start paths call power, firmware download, MAC init, and postinit in sequence.

## Risks

Bring-up ordering is fragile. Power sequence commands are chip/cut/interface-specific and poll hardware state; wrong masks or missing delays can leave the MAC half-powered. Modern firmware download relies on exact firmware section sizes and checksum markers; incorrect header parsing, DDMA source/destination addresses, or register restore failures can prevent firmware boot. Some failure paths after LTE coexistence backup or register backup may not restore every temporary state before returning.

FIFO and queue layout is another high-risk area. Reserved page counts must not exceed TX FIFO pages, and all derived addresses must line up with firmware expectations. Wrong page-table selection for USB bulkout count, PCIe, or SDIO breaks queue scheduling and firmware H2C placement. Queue flushing is best-effort and can time out under heavy traffic.

## Test Signals

Hardware bring-up tests should verify power-on/off across PCIe, USB, and SDIO chips, including already-on retry and SDIO resume polling. Firmware tests should cover modern and legacy images, bad size/checksum images, missing firmware-ready bits, 8821C PCIe BT recovery H2C, and HCI descriptor reset after download. FIFO tests should validate reserved boundaries, H2C queue free-space checks, page table selection by bus/bulkout count, and queue flush behavior under traffic. Channel tests should verify MAC bandwidth, subchannel, CCK check, and timing registers.
