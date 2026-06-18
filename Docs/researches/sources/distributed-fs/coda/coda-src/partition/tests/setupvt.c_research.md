# sources/distributed-fs/coda/coda-src/partition/tests/setupvt.c

Purpose: creates a local test `vicetab` with one simple and one ftree partition entry.

Flow: gets host name, creates `Partent` records for `simpled` and `/tmp/f` with `width=8,depth=5`, recreates `vicetab`, appends both records, frees entries, and prints a reminder to run `makeftree` before continuing.

Risks/test signals: local destructive behavior is limited to unlinking/recreating `vicetab`. It assumes `/tmp/f` and `simpled` setup are handled externally. It validates `Partent_create/add/end` enough for test use.
