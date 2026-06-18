# sources/distributed-fs/lizardfs/src/tools/set_trashtime.cc

Purpose: Implements `lizardfs settrashtime` and deprecated recursive wrapper, changing trash retention time for objects.

Important APIs/types/functions: `set_trashtime_run`; `rset_trashtime_run`; static `set_trashtime`; `CLTOMA_FUSE_SETTRASHTIME`; `MATOCL_FUSE_SETTRASHTIME`; modes `SMODE_SET`, increase, decrease, recursive mask; option `-l`.

Control flow: Parses formatting, recursive, and long-wait flags, parses a numeric seconds argument with optional trailing `+` or `-`, sends a legacy set-trashtime request with inode, uid, value, and mode, then prints direct result or recursive counters.

State and persistence: Mutates master metadata trashtime values. No local persistence.

Dependencies and integration: Uses legacy datapack protocol, common master connection helpers, `my_get_number`-style formatting support, and `mfserr`.

Risks and test signals: Numeric parsing is manual and must catch malformed suffixes and overflow. Recursive mode can affect many inodes. Infinite timeout is represented as `-1` for `tcptoread`. No direct tests in this subset.
