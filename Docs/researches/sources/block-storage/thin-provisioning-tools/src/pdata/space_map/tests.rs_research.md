# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/space_map/tests.rs

Shared tests for `SpaceMap` behavior: block count, allocated count tracking, out-of-space, inc/dec to 255, no duplicate allocation, `set` allocation effects, and wraparound allocation. Applies these to `CoreSpaceMap<u8>`.

Additional metadata-space-map tests verify index-entry count/free-count invariants for single and multiple bitmap cases and tolerate junk bytes in unused metadata-index entries. Disk-space-map tests serialize data maps and verify btree index entry counts and free/allocated totals.
