# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/enc28j60_hw.h

## Purpose

`enc28j60_hw.h` defines the ENC28J60 hardware interface used by `enc28j60.c`: register encodings, register bits, SPI opcodes, status-vector helpers, internal SRAM boundaries, maximum frame length, and LED mode.

## Important Definitions

Register constants combine address bits, bank bits, and `SPRD_MASK` for MAC/MII dummy reads. The file defines all-bank registers, banked buffer/MAC/MII/MAC-address registers, PHY registers, interrupt/status/control bits, RX filter bits, PHY link/duplex bits, packet control bits, TX/RX status-vector bit helpers (`TSV_GETBIT`, `RSV_GETBIT`), and SPI opcodes for control-register, buffer-memory, bit-field, and soft-reset operations.

The internal 8 KiB packet buffer is split with RX at `0x0000..0x19ff` and TX at `0x1a00..0x1fff`. `MAX_FRAMELEN` is 1518, and `ENC28J60_LAMPS_MODE` encodes the preferred LED behavior.

## Control Flow, State, And Dependencies

The header has no executable flow and no stored state. Its constants are used by the driver to generate SPI commands, switch register banks, initialize FIFO pointers, decode status vectors, configure MAC/PHY behavior, and apply errata-sensitive RX behavior. It has only a normal include guard dependency.

## Risks And Test Signals

Bad constants break hardware access globally because bank, register, and dummy-read behavior are encoded together. Buffer boundaries must match the driver FIFO logic. Test through register reads across banks, MAC byte-order programming, RX FIFO wrap, TX/RX status decoding, and warning-clean builds.
