# sources/distributed-fs/coda/coda-src/partition/vicetab.c

Purpose: parser/writer for `/vice/vicetab` partition entries. It hides the `Partent` structure and exposes fstab-like operations.

APIs and flow: `Partent_set/end` open/close files; `Partent_get` skips comments/blanks and tokenizes host, dir, type, options; `Partent_create/add/free` allocate and append entries; accessors return host/type/dir; option helpers search comma/space-separated options and parse integers.

State/persistence: each file line persists one partition entry. `Partent_get` uses a static buffer and `strtok`, so it is not reentrant. Risks include substring option matches (`width` inside another token), fixed 256-byte fields, possible `strtok(NULL)` misuse in `Partent_intopt`, and no robust quoting for paths/options. Test signals come from `setupvt` and `DP_Init`.
