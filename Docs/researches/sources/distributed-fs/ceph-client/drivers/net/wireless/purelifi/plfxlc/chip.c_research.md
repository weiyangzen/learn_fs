<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/plfxlc/chip.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/plfxlc/chip.c

## Purpose
This file implements pureLiFi chip-level control on top of the USB transport. It initializes/releases the chip wrapper, logs hardware identity, sets beacon interval, toggles radio power, enables/disables RX/TX, and writes the selected PHY rate.

## Important APIs, Types, And Functions
Public functions are `plfxlc_chip_init()`, `plfxlc_chip_release()`, `plfxlc_set_beacon_interval()`, `plfxlc_chip_init_hw()`, `plfxlc_chip_switch_radio()`, `plfxlc_chip_enable_rxtx()`, `plfxlc_chip_disable_rxtx()`, and `plfxlc_chip_set_rate()`.

## Control Flow
`plfxlc_chip_init()` zeroes `struct plfxlc_chip`, initializes its mutex, and initializes embedded USB state. `plfxlc_chip_init_hw()` logs USB vendor/product/device version, permanent MAC address, and speed, then programs a default 100 TU beacon interval. Radio and rate changes are sent as USB vendor/write requests. RX/TX enable starts TX first and then RX; disable writes `USB_REQ_RXTX_WR` value zero before shutting down RX and TX queues/URBs.

## State And Persistence
`struct plfxlc_chip` stores the embedded USB transport, mutex, unit type, link LED value, beacon interval, and beacon-set flag. Device-side radio/rate/beacon state persists in firmware until changed, reset, or unplugged.

## Dependencies And Integration Points
Depends on `plfxlc_usb_wreq()`, `plfxlc_usb_enable_tx()`, `plfxlc_usb_enable_rx()`, `plfxlc_usb_disable_rx()`, `plfxlc_usb_disable_tx()`, and `plfxlc_mac_get_perm_addr()`. It is called by `mac.c` during hardware initialization and by `usb.c` during probe and disconnect.

## Risks
Beacon interval caching suppresses duplicate interval writes but ignores `dtim_period` and `type`. Radio/rate writes are synchronous USB bulk requests and can fail during disconnect/reset. RX/TX enable has partial failure risk if TX is enabled and RX enable fails. The chip mutex is initialized but not used in these operations, so callers must provide any needed serialization.

## Test Signals
Probe should log identity and set the default beacon interval. Validate radio on/off, rate setting, RX/TX enable/disable during probe/disconnect, and beacon interval updates from adhoc BSS changes. USB request failures should produce error logs and clean unwind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/plfxlc/chip.c -->
