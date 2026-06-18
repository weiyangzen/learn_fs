# sources/distributed-fs/ceph-client/drivers/media/platform/broadcom/bcm2835-unicam-regs.h

## Purpose
This header defines the Broadcom VC4/BCM2835 Unicam register offsets and bitfields used by the Unicam capture driver.

## Important APIs, Types, and Functions
It defines offsets for core control/status, analogue/lane control, clock/data lane timing, packet compare, image DMA, embedded-data DMA, double-buffering, and miscellaneous registers. Important masks include `UNICAM_CTRL` mode and enable bits, `UNICAM_STA_MASK_ALL`, lane enable/termination/status bits, `UNICAM_ICTL` frame-start/frame-end/line-count interrupts, `UNICAM_IPIPE` pack/unpack fields, image ID fields, embedded-data control bits, and packet compare fields.

## Control Flow
There is no executable flow. `bcm2835-unicam.c` consumes these definitions while starting RX, handling interrupts, programming DMA buffers, configuring packing/unpacking, enabling embedded data, and disabling the hardware.

## State and Persistence
The header defines encodings for volatile MMIO state only. It stores no driver state and persists nothing.

## Dependencies and Integration Points
It includes `linux/bits.h` for `BIT()` and `GENMASK()`. Its definitions are coupled to the Unicam hardware documentation and Broadcom-derived register naming.

## Risks and Edge Cases
Bad masks can break interrupt acknowledgement, lane state, DMA bounds, or pixel packing. Some registers only exist on instances with more than two lanes, so users must guard DAT2/DAT3 access as the driver does.

## Test Signals
Validate register traces for lane enable, interrupt masks/status clearing, image and metadata DMA address programming, `UNICAM_IPIPE` packing modes, and stop/reset sequences.
