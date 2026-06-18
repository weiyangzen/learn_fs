# sources/distributed-fs/glusterfs/xlators/features/changelog/lib/src/changelog-lib-messages.h

Purpose: this header defines structured log message IDs and message strings for `libgfchangelog` and related changelog library code.

Important definitions: `GLFS_MSGID(CHANGELOG_LIB, ...)` reserves IDs for open, rmdir, scratch directory setup, thread creation, opendir, rename, read, htime, write, mmap/munmap, parse, cleanup, notify registration, RPC invocation, event draining, XDR decoding, history failures, and final/requesting status messages. String macros provide stable text for many of these IDs.

Control flow role: changelog library source files use these IDs in `gf_msg` and `gf_smsg` calls to report operational failures and state transitions. The header itself contains no logic.

State and persistence behavior: no direct state. The comments establish a compatibility rule that IDs should be appended and never removed, because log ID reuse breaks diagnostics.

Dependencies and integration points: depends on `glfs-message-id.h` and the `CHANGELOG_LIB` component registration. Operational tooling and tests can key on these IDs.

Risks: editing the ID list incorrectly can break stable logging. Some message strings are broad and shared across multiple source files, so changing them may affect log-based tests.

Test signals: compile all changelog library sources, force failures in rename/open/stat/history/rpc paths, and verify emitted structured message IDs and strings match expectations.
