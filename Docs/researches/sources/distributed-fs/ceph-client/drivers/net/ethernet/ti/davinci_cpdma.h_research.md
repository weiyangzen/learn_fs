# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/davinci_cpdma.h

## Purpose
`davinci_cpdma.h` is the public interface for the DaVinci CPDMA engine. It defines controller parameters, channel statistics, callback types, descriptor status helpers, EOI codes, control enums, and lifecycle/TX/RX function prototypes.

## Important APIs, Types, and Functions
`struct cpdma_params` describes platform resources: device, DMA register windows, HDP/CP/RX free registers, channel count, reset capability, minimum packet size, descriptor memory location/size/alignment, bus frequency, optional descriptor-pool override, and extended-register support. `struct cpdma_chan_stats` records enqueue/dequeue/resource counters useful for diagnostics. `cpdma_handler_fn` is the completion callback signature. The header exposes controller creation/start/stop/destroy, channel create/start/stop/destroy/process/submit, interrupt control, rate and weight configuration, descriptor count tuning, and low-level controls such as `CPDMA_TX_RLIM` and `CPDMA_RX_BUFFER_OFFSET`.

## Control Flow and State
Callers create one `cpdma_ctlr`, then one or more TX/RX channels. RX channels are identified by `rx_type` at creation and submit buffers before or after controller start. State is opaque to callers; all channel/controller internals are hidden behind forward declarations. Status bits exposed through macros are used by completion handlers to interpret RX source port and VLAN encapsulation data.

## Dependencies and Integration Points
The header depends on Linux device, DMA, and bit helper types through included users. DaVinci EMAC supplies `cpdma_params` from platform resources and uses the exported functions in open/stop/NAPI/TX timeout paths. Other TI drivers can share the same abstraction when their hardware matches CPDMA semantics.

## Risks and Test Signals
Because the interface supports both mapped and unmapped buffer submission, callers must match ownership expectations: mapped submit paths require the CPDMA layer to sync rather than unmap. Descriptor count setters can repartition channel resources, so tests should verify RX/TX descriptor accounting after channel creation and after `cpdma_set_num_rx_descs()`. Build coverage should include consumers with and without extended registers and validate enum ordering against `davinci_cpdma.c`.
