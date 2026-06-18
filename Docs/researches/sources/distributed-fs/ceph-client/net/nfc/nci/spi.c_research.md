# sources/distributed-fs/ceph-client/net/nfc/nci/spi.c

## Purpose

This file implements the NFC Controller Interface (NCI) SPI link layer used by NFC controller drivers that expose an SPI transport. It is not a full NCI device driver; it provides reusable send, read, CRC, acknowledge, and allocation helpers around `struct nci_spi` so hardware-specific SPI drivers can move framed NCI packets between the SPI controller and the NCI core.

## Important APIs, Types, and Functions

The exported API is `nci_spi_send()`, `nci_spi_allocate_spi()`, and `nci_spi_read()`. `nci_spi_allocate_spi()` allocates a devm-managed `struct nci_spi`, stores the SPI device, NCI device, acknowledge mode, transfer delay, default controller speed, and initializes `req_completion`. `nci_spi_send()` prepends the four-byte NCI SPI header, optionally appends CRC-CCITT, optionally performs a write-handshake chip-select pulse, sends the skb with `spi_sync()`, and waits for an ACK/NACK when CRC acknowledge mode is enabled. `nci_spi_read()` receives an SPI frame, validates CRC when enabled, completes a pending send request when an ACK/NACK frame is observed, sends ACK/NACK responses, and returns only data payload skbs.

Internal helpers include `__nci_spi_send()` for one SPI transfer, `send_acknowledge()` for ACK/NACK frames, `__nci_spi_read()` for direct-read request plus response transfer, `nci_spi_check_crc()` for CRC validation and trimming, and `nci_spi_get_ack()` for parsing and stripping the SPI response header.

## Control Flow

Transmit flow starts with an NCI skb from the caller. The function pushes the SPI header, appends CRC if `NCI_SPI_CRC_ENABLED`, optionally raises chip select with a zero-length transfer and waits up to one second for a hardware completion, then writes the frame. In acknowledged mode it reinitializes `req_completion` and waits up to `NCI_SPI_SEND_TIMEOUT` for `nci_spi_read()` to observe ACK or NACK from the controller.

Receive flow issues `NCI_SPI_DIRECT_READ`, reads the two-byte response header, derives payload length with or without the CRC length, reads the remaining bytes, and, in CRC mode, pushes the response header back onto the skb so CRC covers the complete frame. After validation it strips header and CRC, completes blocked senders for ACK/NACK-only frames, and returns NULL for pure acknowledge frames.

## State and Persistence

State is held in `struct nci_spi`: acknowledge mode, SPI delay/speed, device pointers, `req_completion`, and `req_result`. There is no durable persistence. Lifetime is tied to the SPI device through devm allocation. Skbs are consumed by send/read paths and freed on completion or error.

## Dependencies and Integration Points

The file depends on Linux SPI core, skb helpers, `crc_ccitt()`, and NCI core allocation constants. It exports symbols for concrete NCI SPI drivers. It integrates with hardware interrupt/handshake logic through an optional completion supplied to `nci_spi_send()` and with the NCI core by allocating skbs against `nspi->ndev`.

## Risks and Edge Cases

Length parsing trusts controller-provided response length after a minimal header read, so allocation pressure and malformed-device behavior matter. CRC mode is critical: bad CRC sends NACK and drops the skb, while ACK/NACK-only frames unblock senders without delivering data. `wait_for_completion_interruptible_timeout()` treats interruption, timeout, and NACK as `-EIO`, which can hide the exact cause. The zero-length chip-select trick depends on controller driver tolerance for a non-NULL buffer with length zero.

## Test Signals

Useful tests include loopback or mocked SPI transfers covering CRC enabled/disabled modes, ACK, NACK, timeout, interrupted wait, malformed CRC, zero-length ACK frames, payload frames with ACK side effects, and write-handshake timeout. Runtime signals are `spi_sync()` errors, send return codes, and correct completion of pending requests.
