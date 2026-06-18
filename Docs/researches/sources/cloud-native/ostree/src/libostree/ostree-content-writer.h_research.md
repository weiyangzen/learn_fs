<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-content-writer.h -->
# sources/cloud-native/ostree/src/libostree/ostree-content-writer.h

## Purpose
Declares the content writer stream type and finish API.

## Important APIs and Types
Defines `OSTREE_TYPE_CONTENT_WRITER`, declares final `OstreeContentWriter` deriving from `GOutputStream`, exposes `_ostree_content_writer_new()` with repo/checksum/uid/gid/mode/content length/xattrs, and `ostree_content_writer_finish()`.

## Control Flow
No runtime flow in the header.

## State and Persistence
Implementation state tracks an open bare repository content write until finish or cleanup.

## Dependencies and Integration Points
Includes `ostree-repo.h`, connecting the stream abstraction to repository storage.

## Risks
The constructor is internal, while finish is the required commit boundary. Callers must not assume close commits content.

## Test Signals
Compile/type checks and stream write/finish integration tests validate this declaration.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-content-writer.h -->
