# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/stripe.c

## Purpose
This file implements the `stripe` ublk target, distributing a single ublk block device across multiple equal-sized backing files using fixed-size chunks.

## Important APIs, Types, and Functions
Types `stripe_conf`, `stripe`, and `stripe_array` describe stripe layout and per-file iovec fragments. Helpers include `calculate_nr_vec()`, `alloc_stripe_array()`, `calculate_stripe_array()`, `stripe_to_uring_op()`, `stripe_queue_tgt_rw_io()`, `handle_flush()`, `ublk_stripe_queue_io()`, `ublk_stripe_io_done()`, `ublk_stripe_tgt_init()`, `ublk_stripe_cmd_line()`, and `ublk_stripe_usage()`.

## Control Flow
Read/write requests are split into one or more per-backing-file iovec runs based on start sector, chunk size, and number of files. The target submits readv/writev SQEs to registered backing file indexes, optionally wrapped in zero-copy buffer register/unregister. Flush submits fsync to every backing file. Initialization validates chunk size, opens all backing files, aligns sizes to chunk boundaries, requires equal sizes, computes aggregate capacity, and sizes SQ/CQ depths by queue depth and file count.

## State and Persistence
Persistent data is striped across backing files. Runtime state includes `stripe_conf` in `dev->private_data` and a per-I/O `stripe_array` freed after completion.

## Dependencies and Integration Points
It depends on `common.c` backing file setup, liburing readv/writev, target ops, and shell tests using `-t stripe`, `--auto_zc`, batch mode, and multiple backing files.

## Risks
All backing files must be equal size after chunk alignment. Integrity and auto-zc fallback are rejected. Incorrect stripe math can corrupt data placement or produce short I/O errors. Zero-copy uses a single buffer index across multiple vector SQEs.

## Test Signals
Mount and fio tests over stripe devices signal correct mapping. Batch and auto-zc tests add coverage for mixed feature paths.
