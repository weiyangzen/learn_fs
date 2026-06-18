
# sources/distributed-fs/ceph-client/drivers/md/dm-log-userspace-transfer.h

## Purpose
Private header for the userspace dirty-log transport layer. It provides the shared message prefix and declares the connector transport lifecycle and request API used by `dm-log-userspace-base.c`.

## Important APIs, Types, And Functions
Defines `DM_MSG_PREFIX` as `dm-log-userspace` for logging. Declares `dm_ulog_tfr_init()`, `dm_ulog_tfr_exit()`, and `dm_consult_userspace(const char *uuid, uint64_t luid, int request_type, char *data, size_t data_size, char *rdata, size_t *rdata_size)`.

## Control Flow
The header has no runtime control flow. The userspace dirty-log module calls `dm_ulog_tfr_init()` before registering its dirty-log type, uses `dm_consult_userspace()` for each daemon request, and calls `dm_ulog_tfr_exit()` during module unload.

## State And Persistence
No state is defined in the header. Transport state is owned by `dm-log-userspace-transfer.c`; log metadata persistence is handled by userspace.

## Dependencies And Integration Points
Consumers must include kernel integer and size definitions through surrounding includes. The declarations bind the userspace dirty-log base implementation to the connector-backed transport implementation and the dm-log-userspace protocol structures from kernel headers.

## Risks
The API exposes raw `char *` payload pointers and value-result sizes, so caller and transport must agree on request-specific layouts and buffer capacities. The header-level `DM_MSG_PREFIX` affects logging in any file that includes it before using dm logging macros.

## Test Signals
Build `dm-log-userspace-base.c` and `dm-log-userspace-transfer.c` together, verify no duplicate message-prefix conflicts, and compile module init/exit paths with connector support enabled.
