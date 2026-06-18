# sources/distributed-fs/ceph-client/drivers/md/dm-verity-fec.c

## Purpose
`dm-verity-fec.c` adds forward error correction to dm-verity. When data or hash verification fails, it uses Reed-Solomon parity data to reconstruct the target block, then revalidates the corrected bytes against the expected verity digest before allowing them to be used.

## Important APIs, Types, and Functions
Important functions include `fec_decode_bufs()`, `fec_read_bufs()`, `fec_decode()`, `verity_fec_decode()`, `__verity_fec_finish_io()`, `verity_fec_status_table()`, `verity_fec_dtr()`, `verity_is_fec_opt_arg()`, `verity_fec_parse_opt_args()`, `verity_fec_ctr_alloc()`, and `verity_fec_ctr()`. It uses `struct dm_verity_fec` for persistent configuration and pools, and `struct dm_verity_fec_io` for per-bio decode state.

## Control Flow
`verity_fec_decode()` is called from dm-verity metadata or data mismatch handling. It lazily allocates per-bio FEC state from mempools, maps metadata blocks into the FEC block namespace when needed, and tries decoding without erasure hints first. If that fails, it reads and hashes related blocks to locate erasures and retries. Decoding deinterleaves message bytes from data/hash regions, reads parity blocks through dm-bufio, calls `decode_rs8()`, writes corrected bytes to an output buffer, and finally hashes the output to prove it matches `want_digest`.

## State and Persistence Behavior
The FEC target state records the parity device, parity start, covered block count, region geometry, hash coverage, RS roots, `rs_k`, bufio clients, mempools, kmem cache, and corrected-block counter. No repaired data is persisted by this file; corrected bytes are copied into the caller's destination buffer for the current bio. Mempool-backed state is released in `__verity_fec_finish_io()`.

## Dependencies and Integration Points
The file depends on dm-verity hash APIs, dm-bufio, dm target parsing, Linux rslib, math helpers, mempools, and kmsg logging. Constructor integration happens through dm-verity optional arguments: `use_fec_from_device`, `fec_blocks`, `fec_start`, and `fec_roots`. Status integration appends the FEC table options and reports corrected counters through the main verity status path.

## Risks and Test Signals
Risks include off-by-one region math, parity reads spanning block boundaries, recursion during metadata recovery, low-memory buffer allocation, and accidentally accepting miscorrected data. Tests should include data-block and metadata-block correction, parity boundary crossing, missing/invalid constructor options, mismatched data/hash block sizes, undersized devices, erasure-assisted recovery, and digest mismatch after RS decode.
