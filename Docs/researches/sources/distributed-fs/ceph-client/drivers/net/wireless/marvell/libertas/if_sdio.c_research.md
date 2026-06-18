# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/if_sdio.c

## Purpose
Implements the SDIO transport for full-firmware Libertas devices, including model detection, firmware/helper download, SDIO register access, command/data/event upload handling, host-to-card queuing, runtime power handling, system suspend/resume, and registration as an `sdio_driver`.

## Important APIs And Functions
`if_sdio_probe()` identifies 8385/8686/8688 models from card info, allocates `struct if_sdio_card`, wires Libertas callbacks into `lbs_private`, and powers on the device. `if_sdio_power_on()`, `if_sdio_prog_firmware()`, `if_sdio_prog_helper()`, `if_sdio_prog_real()`, and `if_sdio_finish_power_on()` perform enablement, firmware status detection, async firmware request, and post-firmware Libertas startup. `if_sdio_interrupt()` handles download acknowledgements and upload interrupts. `if_sdio_card_to_host()` dispatches uploaded packets to `if_sdio_handle_cmd()`, `if_sdio_handle_data()`, or `if_sdio_handle_event()`. `if_sdio_host_to_card()` queues outbound packets for `if_sdio_host_to_card_worker()`.

## Control Flow And State
The driver serializes outbound SDIO writes through a private workqueue and `card->packets`, protected by `card->lock`. IRQ handling reads/clears interrupt cause bits, signals `lbs_host_to_card_done()` on download completion, and pulls one uploaded packet. Power state flows through `priv->fw_ready`, `card->started`, runtime PM reference counts, and `pwron_waitq`. SD8688 removal is special-cased with `user_rmmod` so module unload sends `CMD_FUNC_SHUTDOWN` while surprise card removal does not.

## Dependencies And Integration
Depends on MMC/SDIO core, Linux firmware loading, runtime PM, and Libertas core APIs such as `lbs_add_card()`, `lbs_start_card()`, `lbs_process_rxed_packet()`, command helpers, and power hooks. Firmware names are declared through `MODULE_FIRMWARE` and selected from `fw_table`.

## Risks And Test Signals
Risks include one-transaction transfer requirements, block-size alignment bugs in host controllers, races between IRQ, reset work, and removal, and wait loops around firmware status. Tests should exercise cold firmware load, already-loaded firmware, RX command/data/event paths, SD8688 FUNC_INIT/FUNC_SHUTDOWN, runtime PM power-save/restore, suspend with and without Wake-on-WLAN, and reset-card recovery.
