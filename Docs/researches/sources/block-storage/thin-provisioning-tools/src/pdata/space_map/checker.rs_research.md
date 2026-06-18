# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/space_map/checker.rs

Validates serialized data and metadata space maps against expected in-core counts. `OverflowChecker` walks overflow ref-count btrees and compares each stored count with a supplied `SpaceMap`.

`check_low_ref_counts` reads bitmap blocks, verifies bitmap checksum/type, detects leaks where on-disk count is 1 but expected is 0, reports fatal mismatches, and returns `BitmapLeak` records for repair. Public `check_disk_space_map` and `check_metadata_space_map` gather index entries, count referenced metadata blocks, check overflow trees, and validate low-count bitmaps.
