
# sources/distributed-fs/ceph-client/include/linux/platform_data/huawei-gaokun-ec.h

## Purpose
This header declares the common API for the Huawei Matebook E Go / Gaokun embedded controller driver and its child power-supply and UCSI functions.

## Important APIs And Types
Constants define UCSI CCI/MSGIN read sizes, write size, no-port-update sentinel, smart-charge payload size, module and child device names. Forward declarations cover `gaokun_ec`, `gaokun_ucsi_reg`, and `notifier_block`. Common APIs include notifier registration, raw EC read/write/read-byte helpers. Power-supply APIs include multi-read, byte/word inline reads, smart-charge get/set, and smart-charge enable get/set. UCSI APIs include read/write, register snapshot retrieval, and PAN acknowledge by port.

## Control Flow, State, And Persistence
The header declares synchronous request/response operations around an EC command transport. Children call common helpers to read power-supply registers or UCSI state. Smart-charge settings are likely persistent or semi-persistent in EC firmware, but persistence is implemented by the EC/driver, not the header. Notifiers provide event-driven updates.

## Dependencies And Integration Points
It integrates the Gaokun EC core with notifier consumers, power_supply child device, and UCSI Type-C/USB-C subsystem. The inline word read casts the response buffer to `u8 *`, so callers must account for EC endianness/packing expectations.

## Risks And Test Signals
Risks include fixed-size UCSI payload mismatches, invalid smart-charge payload length, notifier lifetime issues, endian assumptions in word reads, and port id handling for PAN ACK. Test signals include raw EC read/write transactions, power-supply register reads, smart-charge get/set round trip, UCSI PPM command flow, notifier delivery, and invalid-port error handling.
