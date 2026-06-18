# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas_tf/if_usb.h

## Purpose
Defines USB transport protocol constants and device state for the Libertas thinfirm USB driver.

## Important Types And Constants
Message constants match the full USB driver: `CMD_TYPE_REQUEST`, `CMD_TYPE_DATA`, and `CMD_TYPE_INDICATION`. Boot protocol constants define firmware download/update commands and `BOOT_CMD_MAGIC_NUMBER`. `struct if_usb_card` stores USB endpoints, RX/TX/CMD URBs, current RX skb, output buffer, firmware pointer, firmware timeout and waitqueue, firmware sequence/progress fields, CRC and final-block flags, Boot2 version, and the owning `lbtf_private`. Firmware block structs are `fwheader`, `fwdata`, and `fwsyncheader`.

## Control Flow And State
No executable code. The fields are mutated by `if_usb.c` during Boot2 command exchange, firmware block download, normal RX submission, and command/data TX.

## Dependencies And Integration
Includes Linux wait and timer headers and forward-declares `struct lbtf_private`. It is tightly coupled to `libertas_tf/if_usb.c` and the Boot2 firmware image format.

## Risks And Test Signals
Risks include layout drift from firmware expectations, lack of include guard in this header, stale URB pointers on cleanup, and shared `ep_out_buf` reuse. Test signals include successful thinfirm firmware sequencing, valid command/data/indication parsing, and clean USB disconnect after firmware or runtime traffic.
