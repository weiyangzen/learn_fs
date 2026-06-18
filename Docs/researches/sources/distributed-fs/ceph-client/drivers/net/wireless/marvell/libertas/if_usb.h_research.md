# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/if_usb.h

## Purpose
Defines the full-firmware Libertas USB transport ABI and per-device USB state structure used by `if_usb.c`.

## Important Types And Constants
Message types are `CMD_TYPE_REQUEST`, `CMD_TYPE_DATA`, and `CMD_TYPE_INDICATION`. Boot commands include USB firmware download, EEPROM boot, Boot2 update, and firmware update, identified by `BOOT_CMD_MAGIC_NUMBER`. `struct if_usb_card` stores the USB device, URBs, anchors, endpoints, RX skb, output buffer, firmware download state, timeout, waitqueue, surprise-removal flag, and Boot2 version. `struct fwheader`, `struct fwdata`, and `struct fwsyncheader` describe firmware block transport.

## Control Flow And State
The header has no executable code but defines persistent per-device state for both firmware loading and normal runtime. `bootcmdresp`, `CRC_OK`, `fwdnldover`, `fwfinalblk`, and sequence counters are mutated by firmware-load callbacks.

## Dependencies And Integration
Depends on Linux wait queues and timers plus USB/skb types through the implementation. It is tightly coupled to `if_usb.c` and to firmware image layout.

## Risks And Test Signals
Risks include structure layout mismatch with Boot2, insufficient output buffer size for firmware blocks, and stale URB/skb pointers after disconnect. Test signals are valid boot response parsing, firmware block sequencing, and clean URB anchor teardown.
