# sources/distributed-fs/ceph-client/drivers/bluetooth/btmrvl_sdio.c

## Purpose
Implements the Marvell Bluetooth-over-SDIO transport driver. It binds supported Marvell SDIO Bluetooth functions, downloads helper/firmware images, moves HCI/vendor packets between the Bluetooth core and SDIO CMD53 ports, handles card interrupts, supports suspend/resume host-sleep behavior, parses optional wakeup device-tree data, and exposes firmware coredumps for chips that support them.

## Important APIs, Types, And Functions
- `btmrvl_sdio_probe`/`btmrvl_sdio_remove` own SDIO device lifetime and connect this transport to the common `btmrvl` core through `btmrvl_add_card`, `btmrvl_register_hdev`, and callback pointers.
- `btmrvl_sdio_register_dev` enables the SDIO function, claims the SDIO IRQ, sets block size, discovers the I/O port, and configures read-to-clear interrupt behavior for newer chips.
- `btmrvl_sdio_download_helper`, `btmrvl_sdio_download_fw_w_helper`, and `btmrvl_sdio_download_fw` implement firmware boot, including helper transfer, firmware transfer, CRC retry signaling, and multi-function "winner" coordination through firmware status registers.
- `btmrvl_sdio_card_to_host`, `btmrvl_sdio_host_to_card`, `btmrvl_sdio_interrupt`, and `btmrvl_sdio_process_int_status` implement receive, transmit, interrupt capture, and deferred interrupt processing.
- `btmrvl_sdio_suspend`/`btmrvl_sdio_resume` integrate host sleep, MMC keep-power, HCI suspend/resume, and optional wake IRQ handling.
- `btmrvl_sdio_coredump` and `btmrvl_sdio_rdwr_firmware` implement firmware memory dump handshakes via SDIO debug registers and `dev_coredumpv`.

## Control Flow
Module init registers `bt_mrvl_sdio`; probe allocates `btmrvl_sdio_card`, copies device-specific firmware/register metadata from the SDIO ID table, enables and configures the SDIO function, disables interrupts during firmware boot, downloads firmware if the ready signature is absent, enables interrupts, parses wake IRQ data, and registers the HCI device through common Marvell code. TX from the Bluetooth core is routed through `hw_host_to_card`, which aligns/pads the packet and writes to `card->ioport`; RX starts in the SDIO IRQ handler, which snapshots and clears host interrupt status, ORs it into global `sdio_ireg`, then schedules common interrupt handling. The deferred path claims the SDIO host, marks TX ready on download-complete interrupts, and reads one SDIO packet on upload interrupts. Firmware download polls card-ready bits, sends helper chunks with a 4-byte SDIO length header, sends firmware blocks sized by the helper-provided length, and waits for `FIRMWARE_READY`.

## State And Persistence
Per-device state is in `struct btmrvl_sdio_card`: SDIO function, I/O port, firmware names, register map, firmware-download block size, RX unit shift, wake IRQ config, and common `btmrvl_private`. Static `user_rmmod` distinguishes module unload from card removal, and static `sdio_ireg` accumulates interrupt status across IRQ and worker contexts under `priv->driver_lock`. Firmware and helper blobs are transient `request_firmware` resources. Suspend state persists in the common adapter flags `is_suspending`, `is_suspended`, and `hs_state`. Firmware dump memory is staged in `mem_type_mapping_tbl` buffers until handed to devcoredump.

## Dependencies And Integration Points
Depends on Linux SDIO/MMC APIs, firmware loading, device tree IRQ parsing, wakeup PM APIs, Bluetooth HCI core, `devcoredump`, and the Marvell common driver in `btmrvl_drv.h`. It integrates with SDIO IDs for SD8688/8787/8797/8887/8897/8977/8987/8997 devices, HCI statistics, module firmware declarations, MMC keep-power suspend, and common Marvell event filtering via `btmrvl_check_evtpkt` and `btmrvl_process_event`.

## Risks And Edge Cases
The interrupt accumulator is global, so assumptions about one active card matter. Firmware download has several hardware-sensitive timeout paths: zero helper lengths, CRC retry bits, CMD53 write failures, and another SDIO function downloading firmware first. Packet length validation must reject malformed SDIO headers before allocating or passing frames upward. Suspend must undo wake IRQ enablement correctly when the wake IRQ fired and disabled itself. Coredump sizing and register loops trust device-provided memory counts/sizes and need defensive allocation/error handling.

## Test Signals
Useful signals include successful probe with firmware already ready and with full helper/firmware download, TX retry after transient CMD53 failures, RX of HCI event/ACL/SCO/vendor packets with valid and invalid SDIO lengths, read-to-clear and write-to-clear interrupt chips, module unload sending shutdown while surprise removal does not, suspend with and without host-sleep activation, wake IRQ resume behavior, and devcoredump output on supported 8897/89xx hardware.
