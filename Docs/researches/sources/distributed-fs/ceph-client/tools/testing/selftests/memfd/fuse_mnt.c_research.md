# sources/distributed-fs/ceph-client/tools/testing/selftests/memfd/fuse_mnt.c

Purpose: tiny read-only FUSE filesystem exposing `/memfd` with slow direct I/O to force GUP-pinned user pages during reads.

Important APIs/types/functions: implements FUSE callbacks `getattr`, `readdir`, `open`, and `read` through `struct fuse_operations`. Uses `fi->direct_io = 1` and sleeps one second in `read`.

Control flow: only `/` and `/memfd` exist. `/memfd` must be opened read-only. Reads copy from static content after a delay and honor offsets.

State and persistence: no persistent backing store; all data is static in process memory. Mount state exists while the FUSE process runs.

Dependencies and integration points: libfuse, FUSE kernel support, `run_fuse_test.sh`, and `fuse_test.c`.

Risks: FUSE API version 26 is old but intentional for compatibility. Slow reads are by design and can make tests time-sensitive.

Test signals: successful mount makes `./mnt/memfd` available for the GUP/sealing race test.
