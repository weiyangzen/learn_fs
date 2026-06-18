# File Research: sources/block-storage/stratisd/src/engine/sim_engine/filesystem.rs

This file defines the simulator filesystem model.

Persistent/save shape:
- `FilesystemSave` records:
  - name
  - UUID
  - size
  - creation timestamp
  - optional size limit
  - optional origin
  - merge scheduled flag

Runtime type:
- `SimFilesystem` holds:
  - random number for synthetic devnode;
  - creation time;
  - size;
  - optional size limit;
  - optional origin filesystem UUID;
  - merge scheduled state.

Construction and mutation:
- `new()` rejects size limits smaller than filesystem size.
- `set_size_limit()` rejects limits below current size and returns whether the value changed.
- `set_origin()` updates origin and returns whether it changed.
- `set_merge_scheduled()`:
  - no-ops if unchanged;
  - rejects scheduling merge when there is no origin;
  - otherwise updates state.
- `record()` produces `FilesystemSave`.

Trait implementation:
- `devnode()` returns synthetic `/stratis/random-<n>`.
- `path_to_mount_filesystem()` returns synthetic `/somepath/<pool>/<fs>`.
- `used()` reports half the filesystem size.
- `size()`, `size_limit()`, `origin()`, and `merge_scheduled()` expose stored state.

Serialization:
- Converts to JSON with size, used, size limit, and origin strings.

Role in architecture:
- This is the simulator’s `Filesystem` implementation, modeling enough size/origin/merge behavior to test pool and D-Bus workflows.
