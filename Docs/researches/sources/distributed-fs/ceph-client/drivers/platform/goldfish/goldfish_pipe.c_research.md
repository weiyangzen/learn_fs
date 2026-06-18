<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/goldfish/goldfish_pipe.c -->
# sources/distributed-fs/ceph-client/drivers/platform/goldfish/goldfish_pipe.c

## Purpose

This driver implements `/dev/goldfish_pipe`, a fast guest-to-QEMU communication channel for Android Goldfish virtual devices. It opens logical host pipes, passes pinned user pages directly to the emulator, and uses MMIO commands plus interrupts for readiness notification.

## Important APIs, Types, And Functions

`struct goldfish_pipe_command` is the per-pipe command page shared with the host. `struct goldfish_pipe` stores pipe ID, flags, command buffer, mutex, wait queue, parent device, and pinned-page scratch array. `struct goldfish_pipe_dev` stores MMIO base, IRQ, miscdevice, pipe table, and shared device buffers. `goldfish_pipe_read_write()` handles read/write loops. `transfer_max_buffers()` pins pages, populates scatter/gather physical addresses, issues `PIPE_CMD_READ` or `PIPE_CMD_WRITE`, and unpins pages. Interrupt handlers read signalled pipe entries and wake blocked operations. Open/close issue host pipe open/close commands.

## Control Flow

Probe maps the MMIO page, exchanges driver/device versions, allocates shared buffers, registers IRQ and miscdevice, and writes buffer physical addresses to host registers. Opening `/dev/goldfish_pipe` allocates a pipe object and command page, reserves a pipe ID under the device spinlock, provides the command page physical address through the open buffer, and issues `PIPE_CMD_OPEN`. Reads and writes pin user pages in batches of up to 336 buffers, send physical buffer lists to the host, advance by consumed bytes, and wait for host wake events on `PIPE_ERROR_AGAIN` unless nonblocking. Interrupt top half copies signalled pipe IDs/flags into a protected list; threaded handler updates pipe flags and wakes wait queues.

## State And Persistence

All state is runtime-only. Per-pipe state exists from open to release. The global pipe table can grow atomically under spinlock. Host pipe state exists in QEMU and is closed on file release or host-side close. There is no disk persistence.

## Dependencies And Integration Points

It depends on platform MMIO/IRQ resources, miscdevice, user-page pinning, DMA-capable physical addressing, OF compatible `google,android-pipe`, ACPI ID `GFSH0003`, and constants shared with QEMU in `goldfish_pipe_qemu.h`.

## Risks

The driver passes guest physical addresses to the host, so page pinning, dirtying, and unpinning correctness are critical. Device removal frees the pipe table and buffers without explicitly closing open pipes, so open-file lifetime assumptions should be tested. The pipe table grows with `GFP_ATOMIC` while interrupts are disabled. Host protocol version mismatch rejects probe only when older than current device version.

## Test Signals

Test probe resources and version exchange, miscdevice creation, open/close host commands, service name write/read, large transfers crossing many pages, nonblocking `EAGAIN`, wait/wake on read/write, host close behavior, poll flags, IRQ batching above 64 signalled pipes, and module unload with active pipes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/goldfish/goldfish_pipe.c -->
