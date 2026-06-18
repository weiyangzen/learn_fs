<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-content-writer.c -->
# sources/cloud-native/ostree/src/libostree/ostree-content-writer.c

## Purpose
Implements `OstreeContentWriter`, a `GOutputStream` wrapper for writing bare repository content and finalizing it to an OSTree checksum.

## Important APIs and Types
`OstreeContentWriter` stores a referenced `OstreeRepo` and `OstreeRepoBareContent output`. `_ostree_content_writer_new()` opens the bare content destination with expected checksum, metadata, and length. The stream overrides write and close. `ostree_content_writer_finish()` commits the content and returns the actual checksum string.

## Control Flow
Construction initializes repo bare content output. Writes check cancellation and pass buffers to `_ostree_repo_bare_content_write()`, returning the requested count on success. Close intentionally does nothing because callers are expected to call finish. Finalize cleans up repo reference and any unfinished bare content state. Finish commits with `_ostree_repo_bare_content_commit()` and returns a duplicated checksum.

## State and Persistence
Persistent state is the repository object being written through the bare content helper. Until finish commits, output may be temporary/cleanup-managed. Finalize cleans up uncommitted state.

## Dependencies and Integration Points
Depends on autocleanup declarations, `ostree-content-writer.h`, and repo private bare-content APIs. It integrates stream-writing callers with repository object storage.

## Risks
Calling `g_output_stream_close()` is not enough to commit; callers must call `ostree_content_writer_finish()`. The writer returns `count` if the private write helper succeeds, so partial write semantics are hidden inside that helper.

## Test Signals
Tests should cover successful write/finish checksum, cancellation, commit failure, finalize cleanup without finish, metadata propagation, and incorrect expected checksum behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-content-writer.c -->
