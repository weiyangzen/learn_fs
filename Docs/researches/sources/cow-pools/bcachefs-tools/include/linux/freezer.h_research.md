# File Research: sources/cow-pools/bcachefs-tools/include/linux/freezer.h

This header stubs kernel freezer support. `try_to_freeze()` and `set_freezable()` are no-ops, `freezing(task)` is false, and freezable scheduling maps to normal scheduling calls.

`__refrigerator()` is an empty inline. User-space bcachefs-tools has no freezer subsystem.
