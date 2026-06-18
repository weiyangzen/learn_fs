# sources/distributed-fs/ceph-client/drivers/usb/musb/musb_regs.h

## Purpose

`musb_regs.h` is the shared register map and bit-definition header for the MUSB HDRC core. It names common USB, endpoint, bus-control, power, interrupt, CSR, FIFO, ULPI, and test-mode registers and provides small inline helpers for config data and host multipoint address registers. The source was read as a complete 362-line file.

## Important APIs, Types, and Functions

Important definitions include POWER bits, INTRUSB bits, DEVCTL bits, TESTMODE bits, CSR0 peripheral/host bits, TXCSR/RXCSR peripheral and host bits, write-zero-clear masks, type register encodings, CONFIGDATA capability bits, FIFO sizing masks, common register offsets, endpoint register offsets, and bus-control offsets. Inline helpers include `musb_read_configdata`, `musb_write_rxfunaddr`, `musb_write_rxhubaddr`, `musb_write_rxhubport`, `musb_write_txfunaddr`, `musb_write_txhubaddr`, `musb_write_txhubport`, and matching read helpers.

## Control Flow

The header has no standalone runtime flow. Its inline helpers perform ordered register writes/reads through the abstracted `musb_readb/writeb` interfaces and the platform `busctl_offset` callback.

## State and Persistence Behavior

The file defines hardware state bits, not software storage. Values written through these definitions persist in controller registers until changed by software, hardware transfer completion, reset, suspend, or platform power loss.

## Dependencies and Integration Points

The header depends on `tusb6010.h` for an EP0 configuration constant and on MUSB I/O accessors. It is included throughout core, host, gadget, DMA, and platform glue files to keep register semantics consistent.

## Risks and Edge Cases

Incorrect bit masks are high risk because many registers have write-zero-clear behavior and mode-dependent meanings. CSR bits differ between host and peripheral modes, while EP0 reuses TX offsets with special semantics. Platform register remapping must preserve these logical offsets.

## Test Signals

Signals include successful compile across all MUSB platforms, register trace validation during enumeration, host/gadget control transfer tests, FIFO dynamic sizing tests, hub multipoint address tests, suspend/resume transitions, and hardware-specific tests for write-zero-clear behavior.
