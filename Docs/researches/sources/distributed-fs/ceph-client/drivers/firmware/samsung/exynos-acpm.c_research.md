# sources/distributed-fs/ceph-client/drivers/firmware/samsung/exynos-acpm.c

## Purpose
`exynos-acpm.c` is the Samsung Exynos ACPM mailbox protocol core. It maps firmware shared memory, initializes ACPM channels, sends synchronous messages through shared-memory queues and mailbox doorbells, and exposes a managed `acpm_handle` to client drivers.

## Important APIs, Types, And Functions
- Shared-memory descriptors: `struct acpm_shmem` and `struct acpm_chan_shmem`.
- Runtime queues and channel state: `struct acpm_queue`, `struct acpm_rx_data`, `struct acpm_chan`, and `struct acpm_info`.
- Transfer API: `acpm_do_xfer()` is the central message-send function.
- RX/sequence helpers: `acpm_get_saved_rx()`, `acpm_get_rx()`, `acpm_dequeue_by_polling()`, `acpm_prepare_xfer()`, and `acpm_wait_for_message_response()`.
- Queue setup: `acpm_chan_shmem_get_params()`, `acpm_achan_alloc_cmds()`, `acpm_channels_init()`, and `acpm_free_mbox_chans()`.
- Client handle APIs: `devm_acpm_get_by_node()` with internal `acpm_get_by_node()` and `acpm_handle_put()`.
- Probe: `acpm_probe()` maps SRAM, initializes channels, installs PMIC/DVFS ops, registers an ACPM clock platform device, and populates child OF devices.

## Control Flow
Probe resolves the `shmem` phandle, maps the SRAM region, applies match data to find channel init data, reads channel count and queue offsets from shared memory, allocates per-channel state and per-sequence RX buffers, initializes locks, and requests mailbox channel 0 for each ACPM channel. It then installs DVFS/PMIC ops into the handle and registers a platform clock device named by match data.

`acpm_do_xfer()` validates channel and message lengths, rejects interrupt mode because only polling is implemented, locks the TX queue, waits for queue slots, assigns a nonzero sequence number not already in the bitmap, records response expectations, writes the TX words into SRAM, advances TX front, sends a mailbox doorbell, marks TX done, releases the TX lock, and polls RX until the sequence bit clears or timeout expires. RX draining saves out-of-order responses in per-sequence buffers and clears bitmap bits when responses are consumed.

## State And Persistence
The driver stores mapped SRAM pointers, per-channel queue pointers, locks, sequence numbers, pending sequence bitmap, saved RX data, mailbox channels, and a public handle. Firmware/hardware state lives in shared SRAM and ACPM. Device links and module references keep the ACPM supplier alive while consumers hold handles.

## Dependencies And Integration Points
It depends on OF phandles, ioremap, Exynos mailbox messages, mailbox client APIs, shared-memory ACPM firmware layout, child platform population, and PMIC/DVFS helper modules. It exposes functionality through `linux/firmware/samsung/exynos-acpm-protocol.h`.

## Risks
Only polling completion is supported; channels requiring interrupt mode return `-EOPNOTSUPP`. Queue pointer interpretation is inverted from firmware perspective and must match shared memory layout. Sequence numbers range 1..63; bitmap handling must prevent reuse while pending. RX buffer allocation scales with channel message length and sequence count. Timeout paths can leave pending bitmap bits until subsequent cleanup behavior.

## Test Signals
Probe should map SRAM, initialize all channels, request mailboxes, and register the ACPM clock device. PMIC and DVFS operations should complete through `acpm_do_xfer()`. Timeout logs showing channel, sequence, and bitmap identify queue or firmware stalls. Device-link behavior can be tested by consumer probe/remove cycles.
