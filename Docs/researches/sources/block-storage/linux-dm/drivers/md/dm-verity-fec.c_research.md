# File Research: sources/block-storage/linux-dm/drivers/md/dm-verity-fec.c

## Purpose
Adds optional forward error correction for dm-verity using Reed-Solomon codes. When normal hash verification fails for data or metadata blocks, this code reads interleaved source blocks and parity bytes, reconstructs the corrupted block, and revalidates it against the expected verity digest.

## Main Interfaces
- Feature/lifecycle: `verity_fec_is_enabled()`, `verity_fec_ctr_alloc()`, `verity_fec_ctr()`, and `verity_fec_dtr()`.
- Per-bio lifecycle: `verity_fec_init_io()` and `verity_fec_finish_io()`.
- Recovery path: `verity_fec_decode()`.
- Optional-argument handling: `verity_is_fec_opt_arg()`, `verity_fec_parse_opt_args()`, and `verity_fec_status_table()`.
- Internal decode helpers include `fec_decode_rsb()`, `fec_read_bufs()`, `fec_decode_bufs()`, `fec_read_parity()`, and `fec_decode_rs8()`.

## Control Flow
FEC configuration is parsed from optional verity arguments: parity device, covered block count, parity start block, and number of RS roots. `verity_fec_ctr()` validates compatible data/hash block sizes, computes RS data size and interleaving rounds, checks hash/data/FEC device capacities, creates bufio clients, and preallocates RS state, deinterleave buffers, and output buffers through mempools.

During verification failure, `verity_fec_decode()` maps metadata blocks into the FEC-covered block space when needed, computes the base RS block for the corrupted block, and tries correction without erasure hints first. If that fails, it retries with erasure locations found by hashing readable data blocks. Successful correction copies the reconstructed block either to a destination buffer or back into the original bio vectors, then the corrected data is always hashed again and compared with the expected digest.

`fec_read_bufs()` reads each block contributing to an RS block, including data blocks from the data device and hash/metadata blocks from the hash device. It deinterleaves bytes into preallocated RS buffers and optionally records erasures for blocks that fail reads or fail verity hash checks. `fec_decode_bufs()` reads parity bytes and decodes each RS block, collecting the target byte for the corrected output block.

## State And Synchronization
`struct dm_verity_fec` owns the parity DM device, data and FEC bufio clients, FEC layout values, Reed-Solomon parameters, mempools, and buffer cache. Per-bio `struct dm_verity_fec_io` is appended after the variable-length dm-verity per-bio digest fields and tracks allocated RS state, buffer pointers, erasure indexes, output buffer, output position, and recursion level.

## Integration Points
Called from `dm-verity-target.c` when metadata or data verification fails. It uses `verity_hash()`, `verity_hash_for_block()`, `verity_for_bv_block()`, and `verity_io_*()` layout helpers from `dm-verity.h`, plus Linux `rslib`, `dm-bufio`, and DM optional-argument parsing.

## Notable Behaviors
- RS parameters are based on `RS(255, N)` with `N = 255 - fec_roots`; root count is constrained to the supported overhead range.
- Interleaving spreads bytes across rounds to improve recovery from burst corruption.
- Recovery recursion is capped by `DM_VERITY_FEC_MAX_RECURSION` because FEC may need verity hashes, and hash verification itself may require FEC.
- Extra decode buffers are best-effort; at least the preallocated buffer set is required.
- Corrected metadata is written into the dm-bufio buffer passed by the caller, while corrected data can be copied back into bio vectors.

## Risks And Review Focus
- The layout arithmetic connecting data blocks, hash blocks, metadata, parity start, RS block, and interleaving rounds is correctness-critical.
- Erasure detection hashes other blocks during recovery and must avoid uncontrolled recursion.
- Buffer and mempool cleanup must match partial-constructor failure paths through `verity_fec_dtr()`.
- FEC success is only trustworthy after the final verity digest recheck; changes must preserve that validation.
