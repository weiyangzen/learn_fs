# sources/distributed-fs/ceph-client/lib/zlib_dfltcc/dfltcc_deflate.c

Purpose: Implements the DFLTCC-backed deflate hook that can replace software block compression for supported s390 streams while preserving the zlib API and stream state semantics.

Important APIs/functions:
- `dfltcc_can_deflate()` checks command-line support mode, compression parameters, available hardware functions, and format support.
- `dfltcc_reset_deflate_state()` resets common hardware state and initializes level mask and block/DHT thresholds.
- `dfltcc_deflate()` is the hook called from `zlib_deflate()`.
- Internal `dfltcc_gdht()` asks hardware to generate a dynamic Huffman table sample.
- Internal `dfltcc_cmpr()` invokes `DFLTCC_CMPR | HBT_CIRCULAR` and updates stream pointers/counters.
- `send_eobs()` emits hardware-provided end-of-block bits through software bit helpers.

Control flow:
- If hardware cannot be used, the hook returns 0 and software deflate continues. On full flush while declining, it clears hardware history length.
- The hook manages open hardware blocks via `param->bcf`, buffered hardware output via `param->cf`, and dynamic-table renewal when thresholds are crossed.
- It masks excess input so each hardware block is bounded, avoids calling hardware with no output space, and may manually close blocks for non-NO_FLUSH modes.
- On starting a block, it chooses fixed Huffman for the initial small block threshold or generates a DHT for dynamic blocks.
- After CMPR, it maps parameter block fields back into zlib bit buffer/checksum state and sets the software `block_state` result.

State and persistence:
- Uses `struct dfltcc_deflate_state` adjacent to `deflate_state`. It persists hardware parameter block flags, checksum, history, thresholds, and availability.
- `strm->total_in`, `total_out`, `avail_in`, `avail_out`, `next_in`, and `next_out` are updated by hardware call wrappers.
- `state->bi_valid` and `state->bi_buf` bridge sub-byte hardware output with software block/trailer writers.

Dependencies and integration:
- Includes zlib deflate internals, `dfltcc_util.h`, `dfltcc_deflate.h`, s390 setup, and `<linux/zutil.h>`.
- Exported helper symbols allow other code/tests to inspect deflate hardware availability and reset behavior.
- Uses `zlib_tr_send_bits()` and `flush_pending()` from `defutil.h`.

Risks:
- Mixed hardware/software block closing is delicate: incorrect `bcf`, `bhf`, `sbb`, or pending buffer handling can corrupt the deflate bitstream.
- Hardware unsupported-parameter fallback must occur before any hardware output; after partial hardware use, some software fallbacks are impossible.
- Checksum ownership changes when DFLTCC is active, so Adler-32 correctness depends on `param->cv` mapping.
- Threshold and masking logic must ensure progress and avoid livelock with small inputs/output buffers.

Test signals:
- s390 DFLTCC compression tests at level 1, debug all-level mode, unsupported levels/strategies/window sizes, and command-line support modes.
- Flush-mode tests: NO_FLUSH, SYNC/FULL flush, FINISH with open block, and tiny output buffer.
- Verify output against software inflate and independent zlib.
- Test disabling DFLTCC mid-support only before hardware use; after use, ensure failure behavior is explicit.
