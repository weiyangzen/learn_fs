# sources/distributed-fs/glusterfs/xlators/features/compress/src/cdc.c

## Purpose
Implements the `cdc` compression translator, wrapping `readv` and `writev` to compress in one deployment mode and decompress in the opposite mode.

## Important APIs, types, and functions
Primary fops are `cdc_readv` and `cdc_writev` with callbacks. Lifecycle functions are `init`, `fini`, and `mem_acct_init`. `cdc_priv_t` stores zlib window size, mem level, compression level, min size, mode, and debug flag.

## Control flow
`readv` winds to the child and transforms data in the callback: server mode compresses reads, client mode decompresses reads. `writev` transforms before winding: client mode compresses writes, server mode decompresses writes. If data length is zero, below `min-size`, or transform fails, it passes through the original vector. Init validates one child, reads options, normalizes zlib parameters, and requires `mode` to be either `client` or `server`.

## State and persistence behavior
Translator state is only `cdc_priv_t`. Persistent/wire-visible behavior is xdata canary plus compressed bytes/trailer when compression is applied; otherwise data passes through unmodified.

## Dependencies and integration points
Depends on zlib helpers in `cdc-helper.c`, GlusterFS stack APIs, iov length helpers, and xdata dictionaries. It must be paired client/server so the opposite side understands the canary and compression mode.

## Risks and test signals
Risks include transform failure silently passing through in many cases, mismatched client/server placement, compressed write path using original `iobref` while passing generated vectors, and invalid option handling. Tests should cover client-server round trips, server-client read path, min-size threshold, invalid modes/options, corrupted compressed data, and debug mode.
