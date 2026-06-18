# File Research: sources/block-storage/parted/libparted/filesys.c

Implements the global `PedFileSystemType` and alias registries plus generic filesystem probing. Filesystem modules register `PedFileSystemType` objects containing probe callbacks; aliases map alternate or deprecated names onto those types.

`ped_file_system_type_get()` first checks canonical names case-insensitively, then aliases. Deprecated aliases emit a debug message. `ped_file_system_probe_specific()` opens the geometry’s device, calls a single filesystem probe op, closes the device, and returns the detected geometry.

`ped_file_system_probe()` is the ambiguous-detection resolver. It fetches all exceptions while probing every registered filesystem, records up to 32 successful detections and their geometric error from the requested geometry, then chooses the best match only if it is significantly better than all other matches. The significance threshold is `max(4096 sectors, 1% of input length)`. This avoids stale signatures winning when multiple filesystems are partly present.

Risk points are the fixed 32-entry detection arrays and process-global registry mutation. The probe scoring compares only start/end deltas, not semantic confidence.
