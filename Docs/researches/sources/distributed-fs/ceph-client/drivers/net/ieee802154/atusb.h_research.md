# sources/distributed-fs/ceph-client/drivers/net/ieee802154/atusb.h

Purpose: Defines the vendor/product IDs and USB vendor request protocol shared by the Linux ATUSB driver and ATUSB firmware. It is intended to remain identical between kernel and firmware source trees.

Important APIs, types, and constants: `ATUSB_VENDOR_ID` and `ATUSB_PRODUCT_ID` identify Qi Hardware ATUSB devices. `ATUSB_BUILD_SIZE` bounds firmware build-string reads. `enum atusb_requests` assigns request IDs for system status (`ATUSB_ID`, `ATUSB_BUILD`, `ATUSB_RESET`), debug/test/RF control (`ATUSB_RF_RESET`, `ATUSB_POLL_INT`, `ATUSB_TIMER`, GPIO, SLP_TR), transceiver register/buffer/SRAM access, raw SPI helpers, HardMAC RX/TX (`ATUSB_RX_MODE`, `ATUSB_TX`), and EEPROM EUI-64 read/write. Hardware type enum values distinguish ATUSB board revisions, RZUSB, and HULUSB. `ATUSB_REQ_FROM_DEV` and `ATUSB_REQ_TO_DEV` encode USB vendor control request direction.

Control flow: `atusb.c` sends these requests through USB control messages during probe, register access, RF reset, RX mode changes, TX submission, firmware information reads, and EUI-64 retrieval. Firmware interprets `wValue`, `wIndex`, and data lengths according to the comment table in this header.

State and persistence behavior: The header has no runtime state. Some requests affect persistent device EEPROM (`ATUSB_EUI64_WRITE`) or retrieve persistent EUI-64 data (`ATUSB_EUI64_READ`), but the Linux driver only reads EUI-64 in this source set.

Dependencies and integration points: It depends on USB request flag macros supplied by Linux USB headers in users. Its main integration point is the firmware ABI; request numbers and data layouts must remain synchronized with ATUSB firmware.

Risks and edge cases: Changing enum values, directions, lengths, or hardware type numbers breaks compatibility with existing firmware. Comments document expected transfer shapes and are part of the practical ABI. Firmware capabilities vary by version, so drivers must continue gating newer requests such as EUI-64 reads.

Test signals: Compile the ATUSB driver, verify USB device matching, run probe against firmware versions before and after EUI-64 support, confirm request numbers with usbmon traces, and test RF reset, register read/write, RX mode, TX, build string, and EUI-64 read paths.
