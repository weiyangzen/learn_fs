<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/milbeaut-hdmac.c -->
# sources/distributed-fs/ceph-client/drivers/dma/milbeaut-hdmac.c

## Purpose
DMAEngine slave driver for Socionext Milbeaut M10V HDMAC, handling peripheral memory-to-device and device-to-memory scatterlist transfers.

## Important APIs, Types, And Functions
`milbeaut_hdmac_device` owns the DMA device, clock, global base, and flexible channel array. `milbeaut_hdmac_chan` stores a virt-dma channel, current descriptor, channel register base, slave id, and slave config. `milbeaut_hdmac_desc` stores copied SG entries and current SG index. `milbeaut_chan_start` programs source/destination, burst, width, interrupt, and transfer-count registers. `milbeaut_hdmac_interrupt` advances SG entries and completes descriptors. `milbeaut_hdmac_xlate` assigns a slave id from DT arguments.

## Control Flow
Probe counts IRQs to size channels, sets a 32-bit DMA mask, maps registers, enables the clock, fills DMAEngine slave/private callbacks, initializes one channel per IRQ, registers DMAEngine, and registers an OF DMA controller. Prep copies the caller's SG array into driver-owned memory. Issue-pending moves the next descriptor out of the vchan queue and starts the first SG. Each interrupt acknowledges and disables channel IRQ bits, advances the SG index, completes the virt descriptor when all SG entries are done, otherwise starts the next SG. Terminate disables the channel, terminates any active vdesc, collects queued descriptors, and frees them. Remove synchronously terminates every channel before unregistering and disabling the clock.

## State And Persistence
State is per-channel current descriptor, copied scatterlist array, slave config, slave request id, register state, and vchan lists. Hardware global enable and channel registers persist until remove/termination; there is no filesystem persistence.

## Dependencies And Integration Points
Depends on DMAEngine, `virt-dma`, OF DMA custom xlate, platform IRQs, clocks, field-prep register macros, and device-tree compatible `socionext,milbeaut-m10v-hdmac`. Clients pass slave request ids through the DMA specifier and bus widths/bursts through `dma_slave_config`.

## Risks And Edge Cases
Transfer count is computed as `len / (burst * width) - 1`; invalid zero or non-divisible lengths, unset burst, or unsupported burst sizes can underflow or misprogram hardware because prep does not validate them. Residue calculation initializes `txstate->residue` by subtracting the in-flight progress from zero before adding queued SG lengths, which is subtle and can report wrong values if not exactly balanced. Interrupt ack disables EI/CI and relies on restart for the next SG. Remove aborts if `dmaengine_terminate_sync` fails, intentionally warning about possible resource leakage.

## Test Signals
Exercise MEM_TO_DEV and DEV_TO_MEM SG transfers with 1/2/4-byte widths and burst sizes 4/8/16, residue polling during an active SG, pause/resume, terminate active transfer, and DT xlate with valid/invalid one-argument slave ids.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/milbeaut-hdmac.c -->
