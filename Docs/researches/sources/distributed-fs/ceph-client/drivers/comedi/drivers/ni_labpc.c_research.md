# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_labpc.c

## Purpose
`ni_labpc.c` is the ISA bus front end for NI Lab-PC, Lab-PC-1200, Lab-PC-1200AI, and Lab-PC+ boards. It supplies board metadata, legacy attach/detach, I/O region acquisition, and optional ISA DMA initialization, while delegating most hardware behavior to `ni_labpc_common.c`.

## Important APIs, Types, And Functions
`labpc_boards[]` is the board table of `struct labpc_boardinfo`, declaring AI speed, scan-up capability, AO presence, and Lab-PC-1200 register support. `labpc_attach()` requests the ISA I/O range, calls `labpc_common_attach(dev, irq, 0)`, and initializes ISA DMA through `labpc_init_dma_chan()` only when an IRQ was successfully obtained. `labpc_detach()` frees ISA DMA, calls common detach, and releases legacy resources. `labpc_driver` registers board-name based Comedi legacy attachment.

## Control Flow
User-space legacy configuration selects one of the board names and passes I/O base, optional IRQ, and optional DMA channel. Attach reserves 0x20 I/O bytes, invokes the common Lab-PC attach path to allocate private state, register the IRQ, set up timers/subdevices/calibration/EEPROM, and then enables DMA support if both common attach recorded an IRQ and the DMA channel is valid. Detach reverses the optional DMA and common resources before generic legacy detach.

## State And Persistence
This file owns no unique private state. It relies on `struct labpc_private` allocated in common code, and optional `devpriv->dma` allocated by `ni_labpc_isadma.c`. Static board metadata controls persistent capabilities for the attachment.

## Dependencies And Integration Points
It depends on Comedi legacy device configuration, ISA I/O port reservation, `ni_labpc.h` for shared board/private definitions, and `ni_labpc_isadma.h` for optional DMA helpers. It integrates with `labpc_common_attach()` and `labpc_common_detach()`.

## Risks
DMA is initialized only after common attach and only if IRQ registration succeeded, so DMA cannot be used for polled-only devices. If the optional DMA Kconfig helper is disabled, the inline stubs make DMA options silently ineffective. Board metadata drives common behavior; incorrect `is_labpc1200`, `has_ao`, or `ai_scan_up` flags change subdevice layout and command validation.

## Test Signals
Tests should cover all three board table entries, I/O region request bounds, attach without IRQ, attach with IRQ and invalid/valid DMA channel, DMA helper stubs under disabled config, common attach failure propagation, detach ordering, and board flags reflected in common subdevice layout.
