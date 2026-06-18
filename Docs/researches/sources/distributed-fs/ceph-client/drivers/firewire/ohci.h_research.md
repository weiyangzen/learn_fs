<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/ohci.h -->
# sources/distributed-fs/ceph-client/drivers/firewire/ohci.h

Purpose: defines the OHCI 1394 register map, event/status bits, asynchronous transmit DMA data-field helpers, isochronous transmit DMA data-field helpers, and self-ID DMA field helpers shared by the early DMA initializer, the main OHCI driver, and KUnit tests.

Important APIs and control flow: register macros cover global controller state (`Version`, `BusOptions`, `GUIDHi/Lo`, `HCControlSet/Clear`, `IntEvent/Mask`, `LinkControl`, `NodeID`, `PhyControl`, physical request filters), async context bases, and iso transmit/receive context windows. Event macros encode interrupt bits and descriptor event codes used by `ohci.c`. `OHCI1394_PhyControl_Read/Write` helpers package PHY register access commands. AT data helpers operate on little-endian OHCI DMA data quadlets: source bus ID, speed, tlabel, retry, tcode, destination ID, destination offset, and response rcode. IT data helpers similarly encode speed, tag, channel, tcode, sync, and data length for stream packets. Self-ID helpers decode `SelfIDCount` error/generation/size and self-ID receive-buffer generation/timestamp.

State and persistence behavior: no mutable state exists in the header. Its constants and inline helpers define the hardware ABI consumed by register reads/writes and coherent descriptor data in `ohci.c` and `init_ohci1394_dma.c`.

Dependencies and integration points: used by the main OHCI driver, the early physical DMA boot helper, and `ohci-serdes-test.c`. It complements `packet-header-definitions.h` by handling OHCI-specific DMA descriptor data formats, which differ from on-bus IEEE 1394 packet headers.

Risks and test signals: risks include endian mistakes in `__le32` setters/getters, duplicated or stale register masks, wrong event-code translations, and helper bugs corrupting transmitted packets. Some helper expressions rely on callers passing in-range values. Test signals include KUnit `firewire-ohci-serdes` passing, correct async transmit headers on the bus, correct stream-data headers, self-ID completion decoding expected sizes/generations, and no MMIO access regressions in `fw-ohci` probe or interrupt handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/ohci.h -->
