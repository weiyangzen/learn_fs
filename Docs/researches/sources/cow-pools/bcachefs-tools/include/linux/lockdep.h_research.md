# File Research: sources/cow-pools/bcachefs-tools/include/linux/lockdep.h

This header stubs Linux lock dependency tracking. `struct lock_class_key` is empty, and all lockdep acquire/release/class/assert APIs are no-ops or return false.

It keeps lockdep annotations available for compilation, but no runtime validation is performed in bcachefs-tools.
