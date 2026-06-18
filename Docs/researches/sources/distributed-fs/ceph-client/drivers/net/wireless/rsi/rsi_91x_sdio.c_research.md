# sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_91x_sdio.c

## Purpose
This file is the SDIO bus driver for RSI 9113/9116 WLAN devices. It probes SDIO IDs, creates the common RSI core, initializes SDIO function/block/FIFO state, supplies host-interface operations, starts the SDIO RX thread/IRQ path, loads firmware, handles reset/disconnect, and implements SDIO power-management hooks.

## Important APIs, Types, and Functions
Important helpers include `rsi_sdio_set_cmd52_arg`, `rsi_cmd52writebyte`, `rsi_cmd52readbyte`, `rsi_issue_sdiocommand`, `rsi_handle_interrupt`, `rsi_reset_card`, `rsi_setclock`, `rsi_setblocklength`, `rsi_setupcard`, `rsi_sdio_read_register`, `rsi_sdio_write_register`, `rsi_sdio_ack_intr`, `rsi_sdio_write_register_multiple`, `rsi_sdio_host_intf_read_pkt`, `rsi_sdio_reinit_device`, `rsi_sdio_ta_reset`, `rsi_probe`, `rsi_disconnect`, and PM callbacks. `sdio_host_intf_ops` connects this transport to the common HAL.

## Control Flow
Probe calls `rsi_91x_init`, sets `RSI_HOST_INTF_SDIO`, enables the SDIO function, sets block size/clock, initializes slave FIFO registers, determines the device model, starts `rsi_sdio_rx_thread`, claims the SDIO IRQ, then calls `rsi_hal_device_init` to load/boot firmware. Interrupts only wake the RX thread unless firmware is not loaded. Transmit packets go through `rsi_sdio_host_intf_write_pkt`, which maps the RSI queue into a block-count/address encoding and uses Cmd53 writes. Register and firmware-load paths use master-access MS-word selection and Cmd53 reads/writes. Disconnect stops RX, releases IRQ, detaches mac80211/BT, resets the chip/card, disables the function, and deinitializes common state.

## State and Persistence Behavior
The SDIO private object stores `pfunction`, block size, write-failure status, previous descriptor, interrupt/RX counters, buffer-full flags, packet buffer, and RX thread state. The common adapter records SDIO host ops, block size, event-timeout and queue-status callbacks, device model, hibernate/reinit flags, FSM state, and PM state. Hardware state is programmed through CCCR/FBR registers, FIFO controls, watchdog/reset registers, and SDIO master windows; all software state is per-probe.

## Dependencies and Integration Points
It depends on the Linux MMC/SDIO core, `rsi_91x_main.c` lifecycle, `rsi_hal_device_init`, SDIO operation helpers in `rsi_91x_sdio_ops.c`, mac80211 detach/rfkill, optional BT coex, and HAL register constants from `rsi_hal.h`.

## Risks
Manual SDIO card reinitialization in `rsi_reset_card` manipulates host `ios` directly and is sensitive to host-controller behavior. Error paths in interface init can leave `adapter->rsi_dev` allocated until common deinit. `write_fail` suppresses later writes and must be reset only when safe. Suspend sets `fsm_state` to card-not-ready while resume forces MAC-init without a full firmware replay; hibernate paths rely on `hibernate_resume` and later reinit. Register helpers skip host claiming when running in IRQ task context, so context tracking must be correct.

## Test Signals
Probe/remove for both 9113 and 9116 SDIO IDs, Cmd52/Cmd53 read/write failures, IRQ wake and RX packet processing, firmware load over SDIO, buffer-full backpressure, card reset and reload cycles, TA reset, suspend/resume/freeze/thaw/restore/shutdown with WoWLAN, coex attach/detach, and host-controller variants for high-speed/4-bit mode are key signals.
