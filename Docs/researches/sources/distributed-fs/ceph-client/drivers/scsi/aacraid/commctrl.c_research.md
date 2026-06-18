# sources/distributed-fs/ceph-client/drivers/scsi/aacraid/commctrl.c

## Purpose

`commctrl.c` implements the AACRAID management ioctl control path. It lets privileged management tools send raw FIBs or raw SRBs to firmware, subscribe to adapter-initiated FIB events, query driver/PCI/HBA metadata, and request adapter reset. It also delegates container-level ioctls to `aac_dev_ioctl()` in `aachba.c` before handling broader communication-layer commands.

This file is the highest-risk user/kernel boundary in the group. It copies user-controlled structures, validates sizes and SG counts, allocates bounce buffers, maps DMA, sends firmware commands, returns firmware replies, and maintains per-user AIF contexts.

## Important APIs, Types, and Functions

Externally visible function:

- `aac_do_ioctl(struct aac_dev *dev, unsigned int cmd, void __user *arg)`: central ioctl dispatcher, serialized by `dev->ioctl_mutex`.

Important internal functions:

- `ioctl_send_fib()`: copies a user FIB, validates header and sender sizes, optionally allocates a larger coherent FIB for up to 2048-byte requests, sends it synchronously, completes it, and copies the reply back.
- `open_getadapter_fib()`: creates an `aac_fib_context`, assigns a unique 32-bit handle, initializes its completion/list state, and links it into `dev->fib_list`.
- `next_getadapter_fib()`: validates a user context handle, optionally waits for an AIF FIB, copies the next queued adapter FIB to user space, frees the queued copy, and restarts the AIF thread if needed.
- `aac_close_fib_context()` and `close_getadapter_fib()`: free queued FIBs and remove a user AIF context.
- `check_revision()`: reports driver compatibility version/build.
- `aac_send_raw_srb()`: sends a user-provided SCSI request either as legacy SRB passthrough or native HBA command, including user SG copy, DMA mapping, firmware command issue, data copy-back, and reply construction.
- `aac_get_pci_info()` and `aac_get_hba_info()`: copy basic adapter metadata to user space.
- `aac_send_reset_adapter()`: marks adapter shutdown and invokes `aac_reset_adapter()` outside the ioctl mutex.

Local structs include `compat_fib_ioctl`, `aac_pci_info`, and `aac_reset_iop`.

## Control Flow

`aac_do_ioctl()` locks `dev->ioctl_mutex`, rejects commands when `adapter_shutdown` is already set, gives `aac_dev_ioctl()` first chance to handle container-specific requests, and then switches on `FSACTL_*` commands. It unlocks in all exit paths.

`ioctl_send_fib()` allocates a driver FIB, copies the user FIB header first, computes the effective copy size from header `Size` and `SenderSize`, enforces `dev->max_fib_size` or a hard 2048-byte upper bound, and if needed temporarily swaps `fibptr->hw_fib_va` to a larger coherent allocation. `TakeABreakPt` is handled locally by forcing an adapter interrupt. Other commands go through `aac_fib_send()` and `aac_fib_complete()`. The resulting FIB buffer is copied back to user space, and any temporary coherent allocation is released.

The adapter-FIB subscription path starts with `open_getadapter_fib()`, which creates a context and returns an opaque `unique` handle. `next_getadapter_fib()` accepts native and compat ioctl layouts, finds the context under `dev->fib_lock`, returns a queued FIB if one is available, or waits on the context completion if requested. If the AIF thread appears stopped and the adapter is usable, it tries to restart `aac_command_thread()`.

`aac_send_raw_srb()` is the most complex path. It requires `CAP_SYS_ADMIN`, rejects reset state, allocates a FIB, reads the user-provided `count` as the request size, validates it against the expected `user_aac_srb` and SG layout sizes, determines DMA direction from SRB flags, and limits SG count to `HBA_MAX_SG_EMBEDDED`. For native HBA targets identified in `dev->hba_map`, it builds `struct aac_hba_cmd_req`; otherwise it builds an endian-converted `struct aac_srb`. It then allocates kernel bounce buffers for each user SG entry, copies outbound data, maps each buffer for DMA, fills the firmware SG list, sends the command synchronously, copies inbound data back, and copies either an HBA-derived synthetic SRB reply or the firmware SRB reply to user space.

## State and Persistence Behavior

Persistent in-memory state includes:

- `dev->fib_list`, a list of open AIF contexts, protected by `dev->fib_lock`.
- Per-context `fib_list`, `count`, `completion`, `wait`, and `jiffies`, which track queued adapter FIB events and consumer activity.
- `dev->adapter_shutdown`, set by reset ioctl and checked by the dispatcher to block later commands.
- `dev->ioctl_mutex`, serializing ioctl entry points.

The file does not persist state outside memory. User SG buffers are copied into temporary kernel memory and mapped for one command lifetime. Queued AIF FIB copies are heap-allocated and freed when delivered or context-closed.

## Dependencies and Integration Points

This file integrates with user space through `copy_from_user()`, `copy_to_user()`, `memdup_user()`, compat pointer handling, ioctl command constants, and Linux capability checks. It integrates with firmware through `aac_fib_send()`, `aac_hba_send()`, FIB completion/free routines, SRB/HBA structures, and adapter reset. It integrates with event delivery through `aac_command_thread()` and `dev->fib_list`. It calls `aac_dev_ioctl()` for container-specific requests implemented in `aachba.c`.

## Risks and Edge Cases

- `aac_send_raw_srb()` maps DMA buffers with `dma_map_single()` but the visible cleanup path frees `sg_list` buffers without an explicit `dma_unmap_single()`. That deserves focused review against surrounding driver conventions and IOMMU expectations.
- Native-HBA reply copying uses `memcpy(reply.sense_data, err->sense_response_buf, AAC_SENSE_BUFFERSIZE)` while the native sense buffer is `HBA_SENSE_DATA_LEN_MAX`. The current constants are close but not identical; future size changes could create truncation or overflow risk.
- User-provided SG addresses and counts are heavily validated, but this remains a broad privileged attack surface. Boundary tests should cover mixed 32/64-bit SG layouts, zero SG count, oversized count, and invalid copy faults.
- `close_getadapter_fib()` searches `dev->fib_list` before taking `dev->fib_lock`, then locks only for close. Concurrent AIF activity or close/open operations could race.
- `next_getadapter_fib()` returns after dropping the lock and then updates `fibctx->jiffies` outside the protected region, which may be fragile if close races exist.
- `ioctl_send_fib()` trusts firmware-updated FIB contents for copy-back size established before send. Size validation before and after user copy is present, but firmware response size behavior should be tested.
- Reset ioctl intentionally unlocks the ioctl mutex around `aac_reset_adapter()`. That prevents deadlock but allows other state changes during reset; the `adapter_shutdown` flag is the main guard.

## Test Signals

Useful validation includes ioctl fuzzing with invalid sizes and pointers, compat ioctl coverage, CAP_SYS_ADMIN enforcement for raw SRB, successful management FIB send and large-FIB send, AIF open/next/wait/close lifecycle, concurrent AIF consumers, AIF thread restart behavior, raw SRB passthrough on 32-bit and 64-bit SG adapters, native HBA passthrough, DMA mapping fault injection, copy fault injection for inbound/outbound buffers, reset ioctl behavior, and leak/race checks for FIB contexts and SG buffers.
