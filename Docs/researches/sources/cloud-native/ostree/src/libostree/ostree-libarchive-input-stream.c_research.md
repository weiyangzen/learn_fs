# sources/cloud-native/ostree/src/libostree/ostree-libarchive-input-stream.c

## Purpose
This file adapts libarchive entry data into a `GInputStream`. It lets OSTree code consume archive member contents through GLib stream APIs while libarchive remains the underlying reader.

## Important APIs and Control Flow
`G_DEFINE_TYPE_WITH_PRIVATE` defines `OstreeLibarchiveInputStream` as a `GInputStream` subclass with a construct-only pointer property `archive`. `_ostree_libarchive_input_stream_new(struct archive *a)` creates the stream. `ostree_libarchive_input_stream_read()` first honors `GCancellable`, then calls `archive_read_data()`, returning bytes read or mapping libarchive errors into `G_IO_ERROR_FAILED`. `close_fn` is intentionally a no-op returning TRUE; the stream does not own or close the archive.

## State, Dependencies, Integration, Risks, and Tests
State is one borrowed `struct archive *` stored in private data. Dependencies are GObject, GIO, and libarchive. The stream integrates with archive import paths that expect `GInputStream` content sources. Risks are lifetime-sensitive: callers must keep the archive valid and positioned on an entry while the stream is used. The close no-op means archive cleanup belongs to the surrounding archive reader. Test signals should cover successful reads, cancellation, libarchive read errors, and ownership/lifetime behavior when the stream is closed before the archive.
