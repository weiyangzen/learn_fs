# File Research: sources/block-storage/kvdo/vdo/instance-number.h

Tiny public interface for VDO instance-number tracking.

Key responsibilities:
- Declares allocate/release calls.
- Declares module-level initialize and cleanup functions.

Dependencies:
- No includes; uses basic C integer types expected from including context.

Notable risks:
- Does not annotate `vdo_allocate_instance()` as `__must_check`.
