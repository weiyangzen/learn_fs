# sources/cloud-native/ostree/src/libostree/ostree-libarchive-input-stream.h

## Purpose
This private header declares the `OstreeLibarchiveInputStream` GType and constructor used to expose a libarchive reader as a `GInputStream`.

## Important APIs, State, and Integration
It defines type-checking macros, the instance/class structs, the private pointer slot, `_ostree_libarchive_input_stream_get_type()`, and `_ostree_libarchive_input_stream_new(struct archive *a)`. The instance embeds `GInputStream` and stores private state allocated by the implementation. The class includes reserved slots for ABI padding inside the private libostree boundary.

## Dependencies, Risks, and Tests
The header depends on `ostree-libarchive-private.h` and GIO. It is an internal integration bridge between libarchive import logic and GLib stream consumers. Risks are mostly compile-time and ownership-related: the archive pointer is not refcounted by the stream and the header assumes libarchive declarations are available through the private header. Tests should confirm the constructor returns a readable `GInputStream` and that closing it does not destroy the archive.
