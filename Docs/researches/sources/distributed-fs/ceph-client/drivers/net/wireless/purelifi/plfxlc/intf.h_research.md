<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/plfxlc/intf.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/plfxlc/intf.h

## Purpose
This header defines pureLiFi USB vendor request IDs, data alignment constants, firmware metadata lengths, AP station limits, RX status wire format, and the generic USB request wrapper used by control/bulk write helpers.

## Important APIs, Types, And Functions
Definitions include `PURELIFI_BYTE_NUM_ALIGNMENT`, `AP_USER_LIMIT`, FPGA and XL vendor command/request IDs, metadata request IDs, `PLF_SERIAL_LEN`, `PLF_FW_VER_LEN`, `struct rx_status`, `enum plf_usb_req_enum`, and `struct plf_usb_req`.

## Control Flow
No direct runtime flow exists. The values drive firmware download, metadata upload, USB request packet construction, RX status parsing, beacon/rate/power writes, and data TX commands.

## State And Persistence
`struct rx_status` is transient device-to-host metadata prepended to RX frames. `struct plf_usb_req` is a host-to-device request envelope. Constants describe persistent firmware request ABI.

## Dependencies And Integration Points
Included by `usb.h`, which propagates these constants to firmware, USB, chip, and MAC code. The definitions must match the pureLiFi firmware protocol.

## Risks
This header locally defines `ETH_ALEN` instead of relying on the canonical Linux definition, which can conflict if include order changes. Request ids and packed structure layout are firmware ABI and fragile. `PLF_SERIAL_LEN` here is 14, while `usb.h` later defines `PURELIFI_SERIAL_LEN` as 256 for host storage; callers must use the correct length constant.

## Test Signals
Build and sparse checks should catch type/packing drift. Runtime validation comes from successful vendor requests, RX status parsing with sane RSSI/rate/CRC counters, and data/beacon/rate/power writes accepted by firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/plfxlc/intf.h -->
