# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/sdio.h

## Purpose
Defines shared SDIO register offsets, bitfields, generation identifiers, and interrupt metadata used by mt76 SDIO bus code. It is the hardware description companion to `sdio.c` and `sdio_txrx.c`.

## Important APIs, Types, And Functions
The header defines ownership and interrupt registers such as `MCR_WHLPCR`, `MCR_WHISR`, `MCR_WHIER`, mailbox registers, RX packet-length registers, TX queue quota registers, read/write data ports, and CONNAC2-only reset/extended queue registers. `enum mt76_connac_sdio_ver` distinguishes CONNAC and CONNAC2 behavior. `struct mt76s_intr` is the parsed interrupt payload consumed by TX/RX scheduling.

## Control Flow
There is no executable control flow. Consumers use the constants to claim host ownership, enable/disable interrupts, clear WHISR bits, parse RX lengths, update scheduler quotas from WTQCR fields, and choose SDIO-generation-specific aggregation fields.

## State And Persistence
The header describes persistent SDIO function state: host/firmware ownership, interrupt masks/status, mailbox values, queue counters, data ports, RX aggregation mode, reset bits, and per-queue quota counters. `struct mt76s_intr` transiently represents an interrupt snapshot.

## Dependencies And Integration Points
Depends on Linux `BIT`, `GENMASK`, and bitfield conventions. It is included by mt76 SDIO register, IRQ, and TX/RX code, and by chip-specific SDIO drivers that supply `parse_irq()` callbacks.

## Risks
Wrong field selection between CONNAC and CONNAC2 can break ownership, RX aggregation, or queue accounting. The duplicated bit meaning around `WHLPCR_FW_OWN_REQ_SET` and `WHLPCR_IS_DRIVER_OWN` requires careful use by callers.

## Test Signals
Correct parsed ISR bits, RX0/RX1 packet lengths, TX quota refill values, ownership transitions, and reset/interrupt behavior on both CONNAC and CONNAC2 SDIO hardware.
