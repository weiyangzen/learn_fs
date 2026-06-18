# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_common.c

Purpose: safe bounded memory helpers for vidtv's in-kernel MPEG-TS generator.

Important APIs/types/functions: `vidtv_memcpy()` and `vidtv_memset()` validate `to_offset + len <= to_size` before writing, log ratelimited overflow errors, and return the number of bytes actually written.

Control flow: each helper checks the target bounds, returns 0 on overflow, otherwise delegates to `memcpy()`/`memset()` and returns `len`.

State and persistence: no state; helpers are pure wrappers except for logging.

Dependencies and integration points: used by PES, TS, and PSI writers to prevent buffer overruns while constructing MPEG-TS packets in kernel memory. Uses `pr_err_ratelimited()`.

Risks: `to_offset + len` can theoretically wrap `size_t` before comparison; callers mostly use bounded TS sizes, but overflow-safe addition would be stronger. Returning 0 lets writers continue with shorter-than-expected output, so callers must validate packet alignment/byte counts.

Test signals: unit-style boundary tests at exact fit, one-byte overflow, zero length, and writer-level tests verifying mis-sized mux buffers log and avoid writes.
