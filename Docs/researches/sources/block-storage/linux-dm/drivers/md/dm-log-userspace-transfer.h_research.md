# File Research: sources/block-storage/linux-dm/drivers/md/dm-log-userspace-transfer.h

## Purpose
Declares the internal transfer-layer API used by the userspace dirty-log implementation to initialize connector transport, shut it down, and send requests to userspace.

## Main Interfaces
- `dm_ulog_tfr_init()` initializes connector callback state and preallocated transport buffers.
- `dm_ulog_tfr_exit()` unregisters the connector callback and frees transport buffers.
- `dm_consult_userspace()` sends a typed request with optional payload and optional response buffer.

## Control Flow
The header contains no logic; it establishes the contract consumed by `dm-log-userspace-base.c` and implemented by `dm-log-userspace-transfer.c`.

## State And Synchronization
No state is declared here beyond the shared `DM_MSG_PREFIX` macro. Transport state is private to the `.c` implementation.

## Integration Points
Includes `uint64_t`/size-based request arguments and uses request type constants defined by the broader DM userspace-log interface.

## Notable Behaviors
- `rdata_size` is value-result style: input capacity and output used size.
- The UUID and local unique ID identify the userspace log instance for each request.

## Risks And Review Focus
- Callers must pass payload sizes compatible with the transfer implementation’s preallocated limit.
- Response-buffer ownership and lifetime remain with the caller.
