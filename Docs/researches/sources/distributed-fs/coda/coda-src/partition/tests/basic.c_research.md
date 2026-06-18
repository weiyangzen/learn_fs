# sources/distributed-fs/coda/coda-src/partition/tests/basic.c

Purpose: basic manual smoke test for simple and ftree partition backends.

Flow: initializes partitions from local `vicetab`, gets `simpled`, creates an inode, opens it, writes a test string, prints ftree path names, then repeats create/open/write on `/tmp/f`.

Dependencies/risks: uses older API names (`InitPartitions`, `VGetPartition`) rather than current `DP_Init`/`DP_Get`, so it may reflect historical compatibility macros or bitrot. It requires test directories and ftree setup. Test signal is successful create/open/write across both backend types.
