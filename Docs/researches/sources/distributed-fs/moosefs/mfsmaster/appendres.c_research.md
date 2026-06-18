# sources/distributed-fs/moosefs/mfsmaster/appendres.c

This module tracks temporary append reservations by inode. It records a virtual length for an inode while append work is outstanding and removes that reservation once real length catches up or a caller clears it.

The private `appendreservation` node stores `inode`, `vlength`, and `next`. `appendreshash[1024]` is a fixed-size separate-chaining hash table keyed by `inode % 1024`. Public functions are `appendres_getvleng`, `appendres_setvleng`, `appendres_setrleng`, `appendres_clear`, `appendres_cleanall`, and `appendres_init`.

Control flow is simple hash-table mutation. `appendres_setvleng` updates an existing reservation or allocates and prepends a new one. `appendres_getvleng` scans one bucket and returns zero on miss. `appendres_setrleng` removes the reservation when `rlength >= vlength`. `appendres_clear` removes one reservation regardless of length, `appendres_cleanall` frees all buckets, and `appendres_init` zeroes the table.

All state is volatile process memory and is not serialized. Observed integration points are in `filesystem.c`, including setting virtual length and initialization. The module assumes mfsmaster's single-threaded metadata mutation model and has no locking.

Risks include unchecked `malloc`, ambiguity between no reservation and a zero virtual length, linear collision scans, and stale reservations if callers do not clear or advance real length. Test signals should cover insert/update/get, length-based removal, explicit clear, full clean, initialization, and collision behavior.
