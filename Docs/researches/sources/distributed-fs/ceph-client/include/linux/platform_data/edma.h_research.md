
# sources/distributed-fs/ceph-client/include/linux/platform_data/edma.h

## Purpose
This header documents and defines TI EDMA3 platform data. It describes event queues, controller/channel encoding, reserved resources, memcpy channels, queue priorities, crossbar channels, and DMA slave maps.

## Important APIs And Types
`enum dma_event_q` names EDMA event queues and the default queue. `EDMA_CTLR_CHAN()`, `EDMA_CTLR()`, `EDMA_CHAN_SLOT()`, and `EDMA_FILTER_PARAM()` encode controller/channel ids. `struct edma_rsv_info` lists reserved channel and slot ranges. `struct edma_soc_info` supplies default queue, reserved resources, memcpy channel list, queue-priority mapping, crossbar channels, slave map, and slave count.

## Control Flow, State, And Persistence
The header comments describe EDMA control flow: channels trigger transfers and reference PaRAM slots; slots describe transfers and may link to another slot; the channel controller maps logical events to transfer controllers; chained completions can trigger more work. The header itself is declarative. State is static SoC/resource topology plus runtime DMA descriptors in the driver.

## Dependencies And Integration Points
It integrates DaVinci/TI platform code with DMAengine, EDMA channel filters, peripheral slave maps, and consumers such as audio, MMC, SPI, and memcpy clients.

## Risks And Test Signals
Risks include reserved resource overlap, wrong controller/channel encoding, queue priority causing audio glitches, missing xbar mapping, and invalid slave map entries. Test signals include DMA channel filtering, transfer completion on each queue, linked PaRAM transfers, memcpy channel enumeration, reservation enforcement, and high-load peripheral DMA latency.
