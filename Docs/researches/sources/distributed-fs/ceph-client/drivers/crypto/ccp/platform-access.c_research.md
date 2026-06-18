# sources/distributed-fs/ceph-client/drivers/crypto/ccp/platform-access.c

## Purpose

`platform-access.c` implements AMD PSP platform-access mailbox and doorbell transports. It provides serialized firmware message submission for platform services such as HSTI, DBC, and other PSP platform commands.

## Important APIs, Types, And Functions

Exported APIs are `psp_check_platform_access_status()`, `psp_send_platform_access_msg()`, and `psp_ring_platform_doorbell()`, plus lifecycle functions `platform_access_dev_init()` and `platform_access_dev_destroy()`. Helpers `check_recovery()` and `wait_cmd()` poll command-response registers and ready bits.

## Control Flow

Initialization allocates `struct psp_platform_access_device`, stores version register offsets from PSP vdata, and initializes mailbox and doorbell mutexes. `psp_send_platform_access_msg()` locks the mailbox, rejects recovery state, waits for readiness, writes the physical request-buffer address to low/high registers, writes the command field, waits for completion, verifies the address registers still match, and returns either success or `-EIO` with firmware status captured in the request header. The doorbell path similarly serializes, writes a small command/status field, rings the button register, waits, and returns the PSP result.

## State And Persistence Behavior

State persists in `psp->platform_access_data` and consists mainly of MMIO offsets and mutexes. Request buffers are owned by callers; this file only writes their physical address to PSP registers. Hardware command-response registers carry transient command state.

## Dependencies And Integration Points

It depends on PSP master lookup, `linux/psp-platform-access.h` request formats, bitfield helpers, MMIO polling, and register offsets supplied by `sp-pci.c`. DBC and HSTI call into this transport.

## Risks And Test Signals

Risks include mailbox contention with firmware/BIOS users, stale address-register verification failures, timeout handling, and confusing `-EIO` transport errors with firmware-level request failures. Test with platform-access consumers, concurrent command submission, induced PSP busy/recovery states, and dynamic debug hex dumps for request/response payloads.
