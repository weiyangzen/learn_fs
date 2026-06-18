<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/goldfish/goldfish_pipe_qemu.h -->
# sources/distributed-fs/ceph-client/drivers/platform/goldfish/goldfish_pipe_qemu.h

## Purpose

This header defines the guest/host ABI constants shared with QEMU's Goldfish pipe implementation.

## Important APIs, Types, And Functions

It defines enums for pipe poll flags, host error statuses, wake flags, close reasons, per-pipe flag bits, MMIO register offsets, and pipe command codes. Key commands include open, close, poll, read, write, and wake-on-read/write. Key registers include command, signal buffer address/count, open buffer address, version, and get-signalled.

## Control Flow

`goldfish_pipe.c` uses these constants to write MMIO registers, interpret host statuses, build commands, and process host wake events.

## State And Persistence

The header owns no state. It specifies values that both guest and host must treat as stable ABI.

## Dependencies And Integration Points

It is tightly coupled to QEMU's `goldfish_pipe.h` constants and the Goldfish pipe driver.

## Risks

Any numeric mismatch with QEMU breaks communication. Some wake flags such as DMA unlock are defined but not handled by this driver, so host behavior must remain compatible.

## Test Signals

Validate ABI values against the emulator source, probe version negotiation, every command code, every poll flag, and host error conversion in the driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/goldfish/goldfish_pipe_qemu.h -->
