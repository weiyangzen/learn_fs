<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/append-over-page.c -->
# sources/distributed-fs/openafs/src/tests/append-over-page.c

## Purpose
Tests append writes crossing page-sized/cache boundaries and validates read consistency by comparing normal read data to `mmap` data.

## Important APIs, Types, And Functions
Defines large static `long_buf`, `compare_file`, `doit`, and `main`. Uses `open`, `write`, `close`, `fstat`, `read`, `mmap`, `memcmp`, and `err` diagnostics.

## Control Flow
Creates/truncates a file, appends `foobar\n`, closes it, compares read-vs-mmap views, reopens in append mode, writes `long_buf`, closes, and compares again. The optional argv file name defaults to `blaha`.

## State And Persistence
Creates or overwrites the target test file and leaves it present. Allocates temporary read buffers and maps the file read-only.

## Dependencies And Integration Points
Exercises the filesystem/cache manager under test through POSIX append, mmap, read, and close semantics.

## Risks And Test Signals
It does not unmap `mmap_buf`, though process exit reclaims it. Non-ASCII copyright bytes are present in comments. Success is exit `0`; failures identify open/write/read/mmap/compare errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/append-over-page.c -->
