# sources/distributed-fs/ceph-client/lib/zlib_dfltcc/dfltcc.h

Purpose: Defines DFLTCC constants, parameter block layouts, stream extension structures, state-placement macros, and the hardware-enabled predicate used by zlib DFLTCC glue.

Important APIs/types:
- `struct dfltcc_qaf_param` models Query Available Functions results.
- `struct dfltcc_param_v0` models the 1536-byte DFLTCC parameter block for GDHT/CMPR/XPND, including check value, history, block flags, dynamic Huffman table storage, and continuation state.
- `struct dfltcc_state` contains the common parameter block, available-function result, and message buffer.
- `struct dfltcc_deflate_state` extends common state with tuning thresholds and level masks.
- `GET_DFLTCC_STATE()` computes the aligned extension state immediately after inflate or deflate state.
- `is_dfltcc_enabled()` checks the command-line support mode and facility bit 151.

Control flow: Header-only predicates and layout definitions are used by reset and hook functions. `DEFLATE_DFLTCC_ENABLED()` maps to `is_dfltcc_enabled()`.

State and persistence:
- The DFLTCC parameter block persists across streaming calls and carries hardware continuation, history, checksum, and block state.
- `zlib_dfltcc_support` is an external s390 boot/setup control that can disable or restrict deflate/inflate acceleration.

Dependencies and integration:
- Includes `../zlib_deflate/defutil.h`, `<asm/facility.h>`, and `<asm/setup.h>`.
- Layout static assertions enforce hardware ABI size and alignment.
- Shared by DFLTCC deflate and inflate implementations.

Risks:
- Hardware ABI exactness is critical. Bitfield ordering, packing assumptions, offsets, and size must match s390 DFLTCC expectations.
- `GET_DFLTCC_STATE()` relies on the base zlib state being followed by aligned extension storage in the workspace.
- Facility probing must match the architecture; misuse outside s390 is invalid.

Test signals:
- Compile-time static assertions for parameter block size/offset.
- Runtime DFLTCC query on supported hardware.
- Cross-build tests with DFLTCC off to ensure the software path does not include this header.
