# sources/distributed-fs/lizardfs/src/tools/check_file.cc

Purpose: Implements `lizardfs checkfile`, a read-only report of chunk copy counts for one or more files.

Important APIs/types/functions: `check_file_run`; static `check_file`; `CLTOMA_FUSE_CHECK`; `MATOCL_FUSE_CHECK`; `print_number`; human-readable flags `-n`, `-h`, `-H`.

Control flow: Parses formatting flags, opens a master connection per file, sends a legacy check request with inode, reads a response, validates query id and length, then prints either compact 3-byte copy/count entries or an 11-entry 32-bit count table.

State and persistence: Read-only against master state. Mutates only global `humode` for formatting and local buffers.

Dependencies and integration: Depends on `datapack`, `mfserr`, socket helpers, and common tool connection logic. It reports master chunk health/copy accounting.

Risks and test signals: Manual response length interpretation has two protocol formats and rejects unexpected sizes. Buffer allocation trusts the header length. No direct tests in this subset.
