# sources/cloud-native/ostree/src/libostree/ostree-varint.h

## Purpose
Internal header declaring libostree varint read/write helpers.

## Important APIs, Types, And Functions
Declares `_ostree_read_varuint64` and `_ostree_write_varuint64` under `G_BEGIN_DECLS`/`G_END_DECLS`.

## Control Flow
No runtime flow exists in the header. It provides prototypes for code needing compact unsigned integer serialization.

## State And Persistence Behavior
No state is stored. The declarations expose functions whose output may participate in persistent binary formats.

## Dependencies And Integration Points
Depends on GIO/GLib types, particularly `guint8`, `guint64`, `gsize`, `gboolean`, and `GString`.

## Risks
Changing signatures would affect all internal users. The API does not expose a maximum-length constant, so callers must rely on implementation behavior or allocate conservatively.

## Test Signals
Compile coverage plus implementation round-trip tests cover this header.
