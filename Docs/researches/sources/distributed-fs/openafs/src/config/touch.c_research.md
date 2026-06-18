# sources/distributed-fs/openafs/src/config/touch.c

This Windows build utility updates timestamps for files matching a wildcard. `main` calls `_findfirst`/`_findnext`, skips entries whose attributes are not normal files, opens each file read/write binary, seeks to end, writes one null byte, truncates back to the original length with `_chsize`, and closes.

Important functions are `usage` and `main`; the only important constant is `ATTRIBUTE_MASK`, which masks read-only, hidden, system, and directory bits so later Windows attribute bits do not affect the normal-file test. State changes are filesystem timestamp/metadata updates; file contents are intended to remain unchanged.

Dependencies are Windows headers and MSVCRT `_finddata_t`, `_open`, `_lseek`, `_write`, `_chsize`, and `_close`. Integration is Windows make/build rules that need a portable `touch` equivalent. Risks include no open-error checking after `_open`, working only on the current directory component returned by `_findfirst`, and skipping read-only/generated files. Test signals are Windows build rules that depend on timestamp refresh and content-preservation checks for wildcard matches.
