# sources/distributed-fs/ceph-client/fs/befs/io.c

Purpose: converts BeFS inode/block-run addresses to linear disk blocks and reads them with buffer-head I/O.

Important APIs/types/functions: `befs_bread_iaddr`.

Control flow: validates the allocation group against the mounted filesystem, converts run to block number with `iaddr2blockno()`, calls `sb_bread()`, and returns the buffer_head or NULL with diagnostics.

State and persistence: no mutation; reads persistent disk blocks into buffer cache.

Dependencies and integration: used by datastream reads and any code needing BeFS allocation group addressing.

Risks: validation only checks allocation group upper bound; corrupt start/len can still address invalid blocks unless caught elsewhere.

Test signals: read valid root inode and datastream blocks; corrupt allocation group should log an error and fail.
