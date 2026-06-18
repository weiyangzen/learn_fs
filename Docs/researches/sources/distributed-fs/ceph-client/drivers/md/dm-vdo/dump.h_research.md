# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/dump.h

## Purpose
Declares the dm-vdo diagnostic dump interface. It is a small public header used by the DM target and pool dumping code to trigger whole-device dumps and format individual `data_vio` entries.

## Important APIs
`vdo_dump(struct vdo *vdo, unsigned int argc, char *const *argv, const char *why)` parses dump options and emits the requested diagnostic output. It returns `0` on success or `-EINVAL` for unknown options.

`vdo_dump_all(struct vdo *vdo, const char *why)` emits the broadest dump without option parsing, used when a VDO instance is being shut down with dump-on-shutdown enabled.

`dump_data_vio(void *data)` is a callback-style formatter for a `data_vio` object, declared as `void *` so generic pool-dump code can call it without depending on the concrete type.

## Control Flow
`dm-vdo-target.c` includes this header to process `dump` and `dump-on-shutdown` messages. The data_vio pool implementation can use `dump_data_vio()` as a buffer/pool item printer. The header keeps diagnostic functionality separate from core target lifecycle and data-path headers.

## State And Persistence
No state is declared here. The functions read live VDO runtime state and emit logs only; they do not define any on-disk format or persistent metadata behavior.

## Dependencies And Integration Points
The only local include is `types.h`, which provides forward declarations and VDO type names. Integration points are `dm-vdo-target.c`, `dump.c`, and any pool or diagnostic subsystem that needs the `dump_data_vio()` callback.

## Risks
The narrow header surface is low risk. The main API concern is that `dump_data_vio()` accepts `void *`, so callers must pass an actual `struct data_vio *`; misuse would fail at runtime rather than compile time. Because dump output can be large, callers should route these functions only from explicit diagnostic paths.

## Test Signals
Compile coverage from `dm-vdo-target.c` and pool-dump users is the main signal. Runtime checks are successful dmsetup dump messages and shutdown dumps that include data_vio entries when pool details are requested.
