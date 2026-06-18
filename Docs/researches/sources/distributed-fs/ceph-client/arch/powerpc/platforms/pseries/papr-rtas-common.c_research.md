# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/papr-rtas-common.c

## Purpose
Provides common helpers for PAPR RTAS calls that must run a serialized multi-call sequence, collect all result chunks, and expose the immutable result through an anonymous read-only fd.

## Important APIs, Types, And Functions
Blob helpers are `papr_rtas_blob_has_data`, `papr_rtas_blob_free`, `papr_rtas_blob_extend`, and `papr_rtas_blob_generate`. Sequence helpers are `papr_rtas_sequence_set_err`, `papr_rtas_run_sequence`, `papr_rtas_retrieve`, and `papr_rtas_sequence_should_stop`. File interface helpers are `papr_rtas_setup_file_interface`, `papr_rtas_common_handle_read`, `papr_rtas_common_handle_release`, and `papr_rtas_common_handle_seek`.

## Control Flow
Callers provide a `struct papr_rtas_sequence` with optional begin/end callbacks and a work callback. `papr_rtas_retrieve` repeatedly runs complete sequences until success, hard error, or fatal signal; `-EAGAIN` represents firmware start-over. A run invokes begin, repeatedly calls work while it returns data, appends each chunk with `kvrealloc`, invokes end, then either returns the blob or an error. `papr_rtas_setup_file_interface` wraps the completed blob in an anonymous read-only fd.

## State And Persistence
State is per sequence and per returned file: sequence error state, caller params, allocated blob data, and fd private data. Data persists only until the anonymous file is released.

## Dependencies And Integration Points
Used by `papr-indices.c` and `papr-phy-attest.c`, and suitable for similar PAPR sequence calls such as VPD. It depends on anonymous inodes, file descriptor allocation, scheduler signal checks, slab/vmalloc allocation, and simple/fixed-size file helpers.

## Risks And Edge Cases
The first recorded sequence error is preserved. Empty blobs are treated as allocation/data failure. Callers must provide correct locking in begin/end if firmware disallows interleaving. `papr_rtas_blob_generate` returns `ERR_PTR(-EINVAL)` if no work callback is present but otherwise returns NULL for empty/error, which the run path maps to `-ENOMEM` unless the sequence recorded another error.

## Test Signals
Test successful single and multi-chunk sequences, start-over retry, hard errors, fatal signal interruption, missing work callback, empty result, allocation failure, read with offsets, llseek bounds, and release freeing blob memory exactly once.
