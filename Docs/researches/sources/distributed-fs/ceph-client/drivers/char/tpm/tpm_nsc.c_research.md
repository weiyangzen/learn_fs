# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_nsc.c

## Purpose
Supports legacy National Semiconductor TPMs discovered through Super I/O index registers and exposed as a two-byte I/O-port command/data interface.

## Important APIs, Types, And Functions
Private state is `struct tpm_nsc_priv` with base port. Helpers include `wait_for_stat()`, `nsc_wait_for_ready()`, `tpm_nsc_send()`, `tpm_nsc_recv()`, `tpm_nsc_cancel()`, `tpm_nsc_status()`, `tpm_read_index()`, and `tpm_write_index()`.

## Control Flow
Module init probes Super I/O IDs at default and alternate bases, registers a platform driver/device, enables the DPM module, requests the two-port region, allocates a TPM chip, and registers it. Send writes a cancel command as a hardware workaround, waits for ready and input-buffer states, enters normal mode, writes command bytes, and terminates with EOC. Recv waits for F0, checks normal mode, reads bytes until F0/EOC, validates the TPM header size, and returns the response length.

## State And Persistence
State is a platform device pointer and per-chip I/O base. Super I/O configuration persists in hardware while the module is loaded.

## Dependencies And Integration Points
Requires port I/O, platform device registration, TPM core callbacks, and TPM PM suspend/resume helpers.

## Risks And Edge Cases
The driver manually calls remove logic from module exit before unregistering the platform device, so lifetime assumptions are old-style. Back-to-back commands require the cancel workaround. Timeouts are long and polling-based. It reads up to caller `count` before knowing exact response size.

## Test Signals
Super I/O ID detection, base address extraction, region conflict, send/recv mode transitions, cancel behavior, response size validation, and module unload cleanup.
