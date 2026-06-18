# sources/distributed-fs/lizardfs/src/tools/set_eattr.cc

Purpose: Implements `lizardfs seteattr` and `lizardfs deleattr`, changing extra attribute bits for objects, optionally recursively.

Important APIs/types/functions: `set_eattr_run`; `del_eattr_run`; static `set_eattr`; `CLTOMA_FUSE_SETEATTR`; `MATOCL_FUSE_SETEATTR`; option `-f attrname`; modes for set/delete and recursive behavior.

Control flow: Command parsing accumulates attribute bits from repeated `-f` options, parses recursive and formatting flags, validates at least one attribute and one target, then sends a legacy set-extra-attribute request with inode, uid, bitmask, and mode. The response is either status or changed/not-changed/not-permitted counters.

State and persistence: Mutates master metadata extra attribute bits. Global `humode` affects output only.

Dependencies and integration: Uses `eattrtab` names from common tool helpers, legacy packet packing, and master connection logic. Complements `get_eattr.cc`.

Risks and test signals: Attribute name parsing must reject unknown names and combine masks correctly. Recursive mode can touch many inodes. Manual response parsing has no direct tests in this subset.
