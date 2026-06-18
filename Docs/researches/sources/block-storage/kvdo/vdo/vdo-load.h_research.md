# File Research: sources/block-storage/kvdo/vdo/vdo-load.h

This header declares the two VDO load entry points:
- `vdo_prepare_to_load()` reads and decodes on-disk structures without modifying disk state, intended during VDO construction.
- `vdo_load()` performs the operational load/resume sequence and may transition through recovery, read-only, slab scrub, and data-reduction startup phases.

Both return VDO or kernel-style error codes and require VDO/kernel type definitions.
