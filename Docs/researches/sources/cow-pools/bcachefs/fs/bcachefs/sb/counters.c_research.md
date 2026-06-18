# File Research: sources/cow-pools/bcachefs/fs/bcachefs/sb/counters.c

This file implements persistent filesystem counters stored in the superblock and mirrored in per-cpu runtime storage.

Key responsibilities:
- Builds maps from runtime counter enum IDs to stable on-disk IDs.
- Exports counter names, flags, and stable ID maps.
- Renders persisted counter values from the superblock.
- Loads superblock counter values into per-cpu counters and mount snapshots.
- Writes current per-cpu counters back into the superblock counter field, resizing as needed.
- Maintains a delayed-work ring of recent counter snapshots for delta display.
- Initializes and tears down counter storage.
- Resets individual counters.
- Implements the counter query ioctl when chardev support is enabled.

Important invariants:
- Stable on-disk counter IDs are not the same as enum order; mapping tables must be used.
- Counter types distinguish event counts from sector amounts and are enforced by macros in `counters.h`.
- `mount[]` stores the values observed at mount/load time for mount-relative queries.
- Recent counters sample every half second and display only counters that changed across the window.
