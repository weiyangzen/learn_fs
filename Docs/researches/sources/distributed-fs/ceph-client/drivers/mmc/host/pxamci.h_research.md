# sources/distributed-fs/ceph-client/drivers/mmc/host/pxamci.h

## Purpose
`pxamci.h` defines the PXA MCI register offsets and bit masks consumed by `pxamci.c`. It is a hardware contract header, not an independent driver.

## Important APIs, Types, And Functions
The header exposes register offsets such as `MMC_STRPCL`, `MMC_STAT`, `MMC_CLKRT`, `MMC_CMDAT`, `MMC_I_MASK`, `MMC_I_REG`, `MMC_CMD`, argument/response registers, and FIFO ports. It defines command/power/control bits such as `STOP_CLOCK`, `START_CLOCK`, `CMDAT_DMAEN`, `CMDAT_INIT`, `CMDAT_DATAEN`, `CMDAT_WRITE`, and response type encodings. It also defines status and interrupt bits for command response, program done, data transfer done, FIFO service, SDIO, and errors.

## Control Flow
There is no executable control flow. `pxamci.c` uses these constants to stop/start the clock, configure command attributes, unmask interrupts, read status, and access FIFOs.

## State And Persistence
The header stores no state. Its conditional `MMC_I_MASK_ALL` value depends on build configuration for PXA27x/PXA3xx versus older PXA targets, shaping the runtime driver's default interrupt mask.

## Dependencies And Integration Points
The sole integration point is inclusion by the PXA MCI driver. The constants mirror the controller programming model and must stay synchronized with the implementation's command, DMA, IRQ, and FIFO handling.

## Risks And Test Signals
Risks are incorrect bit definitions or build-conditional masks causing missed/unexpected interrupts or wrong command modes. Test signals are indirect: successful PXA command/data/SDIO operation, clock control, FIFO service, and error decoding in `pxamci.c`.
