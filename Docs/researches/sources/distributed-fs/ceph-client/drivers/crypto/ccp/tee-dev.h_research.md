# sources/distributed-fs/ceph-client/drivers/crypto/ccp/tee-dev.h

## Purpose

`tee-dev.h` describes the host/AMD Secure Processor TEE ring-buffer ABI and declares TEE device lifecycle functions.

## Important APIs, Types, And Functions

It defines `struct tee_init_ring_cmd`, `struct ring_buf_manager`, `struct psp_tee_device`, `enum tee_cmd_state`, `enum cmd_resp_state`, and packed `struct tee_ring_cmd`. Constants include `TEE_DEFAULT_CMD_TIMEOUT`, `TEE_DEFAULT_RING_TIMEOUT`, `MAX_BUFFER_SIZE`, and `MAX_RING_BUFFER_ENTRIES`. It declares `tee_dev_init()`, `tee_dev_destroy()`, and `tee_restore()`.

## Control Flow

There is no executable flow. The declared ring-entry states are used by `tee-dev.c` and PSP firmware to coordinate command lifecycle.

## State And Persistence Behavior

The ring manager stores host-maintained write pointer and firmware-visible ring address. Each ring entry stores command state, PSP status, payload, and driver response flag.

## Dependencies And Integration Points

It depends on Linux device/mutex types and PSP TEE command IDs from public headers included by the implementation. The ABI is shared with firmware, so packing and 1024-byte entry size are significant.

## Risks And Test Signals

Risks include structure size/layout drift, incorrect state transitions, and buffer-size mismatch with callers. `BUILD_BUG_ON(sizeof(struct tee_ring_cmd) != 1024)` plus live TEE command round trips are the main signals.
