# sources/distributed-fs/glusterfs/xlators/performance/io-cache/src/io-cache-messages.h

## Purpose
Defines stable log message IDs and reusable message strings for the io-cache translator.

## Important APIs, types, and functions
`GLFS_MSGID(IO_CACHE, ...)` allocates message identifiers such as `IO_CACHE_MSG_NO_MEMORY`, `IO_CACHE_MSG_PAGE_FAULT`, `IO_CACHE_MSG_SERVE_READ_REQUEST`, and `IO_CACHE_MSG_DEFAULTING_TO_OLD`. The `_STR` macros provide human-readable text for common logging paths.

## Control flow
No control flow is implemented. C files include this header and pass the IDs to `gf_smsg()` or `gf_msg()` on allocation, validation, configuration, and cache fault errors.

## State and persistence behavior
Message IDs are part of Gluster's externally visible log compatibility surface. The comments require append-only changes to prevent ID reuse.

## Dependencies and integration points
Depends on `glfs-message-id.h` and the global `IO_CACHE` component registration. It integrates with structured logging, downstream log parsers, and support tooling that keys off message IDs.

## Risks and test signals
Risks are deleting/reordering IDs, misspelled strings, and logging an ID for the wrong component. Test signals are compile-time inclusion, message catalog consistency checks, and log assertions on representative io-cache error paths.
