# sources/distributed-fs/ceph-client/drivers/nfc/st95hf/spi.c

## Purpose

This file implements the low-level SPI transport functions used by the ST95HF NFC driver. It is intentionally small: it serializes SPI access, sends ST95HF command buffers, waits for synchronous interrupt completion when requested, and reads normal or echo responses from the chip.

## Important APIs, types, and functions

The public functions are `st95hf_spi_send()`, `st95hf_spi_recv_response()`, and `st95hf_spi_recv_echo_res()`, all exported with `EXPORT_SYMBOL_GPL` and declared in `spi.h`. They operate on `struct st95hf_spi_context`, especially its `spidev`, `done`, `spi_lock`, and `req_issync` fields.

`st95hf_spi_send()` builds a single transmit `spi_message`, marks whether the request is synchronous, sends it with `spi_sync()`, and for `SYNC` requests waits up to 1000 ms for the IRQ handler to complete `done`. `st95hf_spi_recv_response()` first transmits the ST95HF receive command and reads the two-byte response header, computes the full response length including long-frame support using header bits `0x60`, then issues a second SPI transfer for the remaining payload. `st95hf_spi_recv_echo_res()` performs the one-byte echo response read sequence.

## Control flow and state behavior

All three functions hold `spicontext->spi_lock` around SPI bus operations, so the higher-level driver can interleave synchronous configuration commands and asynchronous data exchange without concurrent bus transactions. `st95hf_spi_send()` sets `req_issync` before sending; the top-half IRQ handler in `core.c` checks that flag and completes `done` for synchronous commands. Asynchronous sends return as soon as `spi_sync()` completes, leaving response handling to the threaded IRQ path.

The response reader writes into a caller-provided buffer and returns the total response length. It does not allocate memory or persist state outside `req_issync`.

## Dependencies and integration points

The implementation depends on the Linux SPI API and on the IRQ/completion convention in `core.c`; without the ST95HF IRQ handler completing `done`, synchronous sends time out. It also relies on ST95HF command codes from `spi.h`.

## Risks and edge cases

The response length computed from the chip header is trusted and there is no local maximum-buffer check in `st95hf_spi_recv_response()`. Callers must pass a buffer large enough for the device-reported length. `req_issync` is protected by the SPI lock during send but read from IRQ context without that lock, so ordering depends on command/IRQ sequencing and normal completion semantics. A missing IRQ for synchronous commands causes a fixed one-second timeout.

## Test signals

Tests should cover SPI send failures, synchronous timeout, successful IRQ completion, echo reads, normal short responses, long-frame response length calculation, and concurrent callers contending on `spi_lock`. Hardware traces should show the receive command followed by a two-byte header read and then a payload read of exactly the computed length.
