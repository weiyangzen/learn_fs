# File Research: sources/block-storage/kvdo/vdo/vdo-load.c

This file implements VDO pre-load and load state machines. Load phases include start, stats/sysfs setup, depot load/recovery/rebuild, marking dirty, allocation prep, slab scrubbing, data reduction startup, finished, journal draining, and waiting for read-only transition.

Pre-load path:
- `vdo_prepare_to_load()` runs admin operation `PRE_LOAD`.
- `pre_load_callback()` starts pre-loading on the admin thread, reads the super block from the data-region start, then `vdo_load_components()` decodes component state.
- `decode_vdo()` decodes/validates super-block state, checks block-map maximum age against recovery journal length, creates read-only notifier and entry, decodes recovery journal, slab depot, block map, logical zones, physical zones, and hash zones.

Load path:
- `vdo_load()` runs admin operation `LOAD`, logs start/started, and treats `VDO_READ_ONLY` as a usable read-only start.
- `load_callback()` advances through phases on the admin thread except journal drain, which is routed to the journal thread.
- It opens the recovery journal, enables read-only entry, initializes sysfs/kobjects, chooses normal/recovery/read-only rebuild depot loading, marks the volume dirty and saves components, initializes block map from journal, prepares slabs for allocation, enters recovery mode if needed, scrubs unrecovered slabs, starts compression/dedupe as configured, and completes admin state.

Error behavior:
- `handle_load_error()` attempts to bring the device online read-only on load errors.
- During read-only rebuild failure at the make-dirty phase, it preserves the error and drains the journal before finishing.
- If final load fails outside success/read-only, `vdo_load()` suspends the VDO into an unresumable stopping state.

The file ties together super-block/component decoding, recovery decisions from `vdo_state`, sysfs initialization, slab depot recovery, read-only notifier behavior, and data-reduction startup.
