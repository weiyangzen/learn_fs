# sources/distributed-fs/ceph-client/drivers/crypto/ccp/tee-dev.c

## Purpose

`tee-dev.c` implements the AMD PSP Trusted Execution Environment ring-buffer interface. It initializes a shared command ring with PSP firmware and exports a kernel API for submitting TEE commands through the PSP master device.

## Important APIs, Types, And Functions

Public APIs are `tee_dev_init()`, `tee_dev_destroy()`, `tee_restore()`, `psp_tee_process_cmd()`, and `psp_check_tee_status()`. Ring helpers include `tee_alloc_ring()`, `tee_free_ring()`, `tee_alloc_cmd_buffer()`, `tee_init_ring()`, `tee_destroy_ring()`, `tee_submit_cmd()`, and `tee_wait_cmd_completion()`. Static `psp_dead` disables further TEE use after fatal timeout/error.

## Control Flow

Initialization allocates a ring of 32 `tee_ring_cmd` entries, sends `PSP_CMD_TEE_RING_INIT` with the physical ring address, retries once by destroying a busy ring after hibernate-like conditions, and stores state in `psp->tee_data`. Command submission locks the ring, waits for an empty entry, rejects if PSP is dead, writes command ID/state/payload, advances the write pointer, rings firmware through the write-pointer MMIO register, then waits for firmware to mark the command completed. The response payload and status are copied back and the entry flag is marked copied.

## State And Persistence Behavior

Persistent state is `struct psp_tee_device` and its `ring_buf_manager`: ring virtual address, physical address, size, mutex, and write pointer. Firmware owns the read pointer register and updates command state in-place. Fatal command timeout or destroy/init failure sets `psp_dead` until driver reload.

## Dependencies And Integration Points

It depends on PSP mailbox commands, TEE register offsets in `tee_vdata`, `linux/psp-tee.h` command IDs, PSP master lookup, and PSP restore during PCI restore.

## Risks And Test Signals

Risks include ring full handling under concurrency, cache coherency of firmware-updated ring entries, timeout disabling all TEE operations, copying more than `MAX_BUFFER_SIZE`, and ring reinitialization after hibernate. Test with TEE clients using `psp_tee_process_cmd()`, concurrent submissions, forced full ring, hibernate restore, firmware busy response, and timeout injection.
