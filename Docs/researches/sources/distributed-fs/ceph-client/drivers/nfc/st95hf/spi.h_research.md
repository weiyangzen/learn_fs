# sources/distributed-fs/ceph-client/drivers/nfc/st95hf/spi.h

## Purpose

This header defines the ST95HF SPI transport interface shared between the core ST95HF NFC driver and the transport implementation. It centralizes command opcodes, reset length, synchronous/asynchronous request typing, the SPI context structure, and function prototypes.

## Important APIs, types, and functions

The basic ST95HF SPI commands are `ST95HF_COMMAND_SEND`, `ST95HF_COMMAND_RESET`, and `ST95HF_COMMAND_RECEIVE`; `ST95HF_RESET_CMD_LEN` documents the one-byte reset command length. `enum req_type` distinguishes `SYNC` commands, which require IRQ completion before returning, from `ASYNC` commands, whose responses are handled later. `struct st95hf_spi_context` stores `req_issync`, `struct spi_device *spidev`, `struct completion done`, and `struct mutex spi_lock`.

The prototypes are `st95hf_spi_send()`, `st95hf_spi_recv_response()`, and `st95hf_spi_recv_echo_res()`.

## Control flow and state behavior

The header has no executable control flow but defines the state contract used by `core.c` and `spi.c`: the core driver initializes the completion and mutex, the send helper updates `req_issync`, and the IRQ handler completes `done` for synchronous transactions.

## Dependencies and integration points

It depends only on `<linux/spi/spi.h>` for SPI device definitions and indirectly on completion/mutex declarations from kernel headers included by that path. It is private to the ST95HF driver directory and should remain aligned with the transport behavior in `spi.c`.

## Risks and edge cases

Any change to `enum req_type` or `struct st95hf_spi_context` must be kept consistent with both IRQ-side and SPI-side code. Because the context embeds synchronization objects, callers must initialize it before any send/receive call and must not copy it after initialization.

## Test signals

Compile coverage of the ST95HF module is the main signal for this header. Runtime tests should indirectly verify that the `SYNC`/`ASYNC` split and completion state defined here match actual command behavior.
