# File Research: sources/block-storage/kvdo/vdo/slab-scrubber.h

Defines the slab scrubber type and public API.

`struct slab_scrubber` contains:
- Completion for current scrub operation.
- High-priority and normal slab lists.
- Wait queue for callers waiting on scrubbed slabs.
- Cross-thread queried `slab_count`.
- Admin state.
- High-priority-only mode flag.
- Read-only notifier.
- Current slab.
- Metadata VIO and buffer for reading slab journal data.

Exports:
- Create/free scrubber.
- Register slabs for normal or high-priority scrubbing.
- Scrub all slabs or high-priority slabs.
- Stop/resume scrubbing.
- Queue clean-slab waiters.
- Query scrubber slab count and dump diagnostics.
