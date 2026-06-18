<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/omap-mcpdm.h -->
# sources/distributed-fs/ceph-client/sound/soc/ti/omap-mcpdm.h

## Purpose
Private/public McPDM definition header. It provides register offsets, bitfields, thresholds, offset-cancellation macros, and the machine-driver helper prototype for configuring downlink offsets.

## APIs, Types, and Functions
Defines McPDM register addresses for IRQ, DMA, control, data, FIFO, and offset registers; IRQ and DMA bits; uplink/downlink channel mask macros; reset/watchdog/output format bits; FIFO threshold maxima; downlink RX1/RX2 offset enable/value macros; and `omap_mcpdm_configure_dn_offsets()`.

## Control Flow, State, and Persistence
No logic executes in the header. The macros determine how `omap-mcpdm.c` persists channel masks and offset values in hardware registers; the exported function lets a machine driver set per-codec trim-derived offsets before stream start.

## Dependencies and Integration
Included by `omap-mcpdm.c` and `omap-abe-twl6040.c`. The function prototype depends on ASoC runtime type visibility through included build context.

## Risks and Test Signals
Risks include channel-number macros assuming one-based channel indexes, offset fields silently masking to five bits, and consumers depending on exact CTRL bit layout. Test signals are build coverage, McPDM link-mask programming for all channel counts, and TWL6040 trim offset writes being visible in `MCPDM_REG_DN_OFFSET`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/omap-mcpdm.h -->
