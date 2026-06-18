# File Research: sources/cow-pools/bcachefs-tools/raid/test.h

This header declares the RAID test entry points implemented in `test.c`.

Declared tests:
- `raid_test_insert()`
- `raid_test_sort()`
- `raid_test_combo()`
- `raid_test_rec(unsigned mode, int nd, size_t size)`
- `raid_test_par(unsigned mode, int nd, size_t size)`

The header documents that recovery tests grow exponentially with disk count because they enumerate failure combinations.
