# File Research: sources/block-storage/util-linux/libmount/src/iter.c

This file implements libmount's small generic iterator object used to traverse internal lists and tables forward or backward.

Key APIs:

- `mnt_new_iter(direction)` allocates an iterator and stores the direction.
- `mnt_free_iter()` frees it.
- `mnt_reset_iter(itr, direction)` clears iterator state and either applies a new direction or preserves the old one when passed `-1`.
- `mnt_iter_get_direction()` returns the current direction.

Dependencies and interactions:

- Used heavily by table and option-list traversal code, including umount iteration, fstab/utab scans, and hook option scans.

Risk notes:

- `mnt_reset_iter()` assumes `itr` is non-null; the public header marks it nonnull.
