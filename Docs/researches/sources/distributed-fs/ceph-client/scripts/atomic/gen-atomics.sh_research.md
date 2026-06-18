# sources/distributed-fs/ceph-client/scripts/atomic/gen-atomics.sh

## Purpose
`gen-atomics.sh` orchestrates regeneration of all generated atomic headers and Rust atomic helper C source.

## APIs, Types, And Functions
It defines `ATOMICDIR`, `ATOMICTBL`, and `LINUXDIR`, then uses a here-document mapping generator scripts to output paths. It invokes each script with `/bin/sh`, redirects to `include/<header>`, computes `sha1sum`, and appends the hash as a comment.

## Control Flow
The script iterates over four rows: instrumented header, atomic-long header, arch fallback header, and Rust helper source. Each output is regenerated from `atomics.tbl` and then annotated with its content hash.

## State And Persistence
It writes persistent generated files under `include/linux/atomic/` and `include/../rust/helpers/atomic.c` relative to the kernel tree.

## Dependencies And Integration Points
It depends on the other atomic generator scripts, `atomics.tbl`, `sha1sum`, and expected tree layout. It integrates with maintainer workflows for checking in regenerated atomic artifacts.

## Risks And Test Signals
Risks include path assumptions, partial regeneration on script failure, and hash churn when generator output changes. Test signals are deterministic regenerated files and matching appended hashes.
