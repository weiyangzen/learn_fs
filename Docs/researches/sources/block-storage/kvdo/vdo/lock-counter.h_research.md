# File Research: sources/block-storage/kvdo/vdo/lock-counter.h

Public API for VDO lock-counter sets.

Key responsibilities:
- Documents the per-zone reference-count locking model and notification contract.
- Declares creation/free, lock-state query, journal initialization, acquire/release operations, journal release operations, acknowledge, suspend, and resume.

Dependencies:
- Includes completion and VDO types.

Notable risks:
- The owner callback must understand that notification means “some lock may be released”, not which lock.
- Correct use depends on thread-context constraints documented in the `.c` file more than in the signatures.
