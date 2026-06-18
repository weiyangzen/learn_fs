<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/plfxlc/usb.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/plfxlc/usb.h

## Purpose
This header declares the pureLiFi USB transport ABI, supported device IDs, endpoint IDs, firmware constants, RX/TX state structures, station queue state, timers, and public USB helper APIs.

## Important APIs, Types, And Functions
Definitions include USB vendor/product IDs for X/XC/XL, firmware buffer sizes and magic values, endpoint IDs `EP_DATA_IN` and `EP_DATA_OUT`, RX URB count, station FIFO/status message ids, station flag bits, `struct plfxlc_usb_rx`, `struct plf_station`, `struct plfxlc_firmware_file`, `struct plfxlc_usb_tx`, and `struct plfxlc_usb`. Inline helpers convert USB/interface pointers to `usb_device` and `ieee80211_hw`.

Public prototypes cover sync/async writes, TX completion, USB init/release, RX/TX enable/disable, hardware init, speed naming, firmware download, and metadata upload.

## Control Flow
The header itself has no major execution path, but its inline conversions are used by USB callbacks and chip/MAC helpers. Its structures drive RX URB allocation, station queue scheduling, and device probe state.

## State And Persistence
`struct plfxlc_usb` is embedded in `struct plfxlc_chip` and persists for the `ieee80211_hw` lifetime. It owns RX URB arrays, TX station queues, timers, interface references, flags, and link state. `struct plfxlc_firmware_file` is transient metadata for packed XL firmware parsing.

## Dependencies And Integration Points
Includes Linux completion/netdevice/spinlock/skbuff/USB headers and `intf.h`. It is included by chip, mac, firmware, and usb implementation files.

## Risks
The header declares `int plfxlc_usb_tx()` but this function is not implemented in the viewed source set, so callers would fail to link if introduced. `DEVICE_LIFI_XC` and `DEVICE_LIFI_XL` share value 1, which is fine if only informational but ambiguous if logic later distinguishes them. Host storage `PURELIFI_SERIAL_LEN` is 256 while firmware serial length in `intf.h` is 14. Timer and queue state must be initialized exactly once during probe.

## Test Signals
Compile/link coverage should catch stale prototypes. Runtime validation includes endpoint use, station queue flags, timer behavior, firmware file metadata handling, and correct USB ID matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/plfxlc/usb.h -->
