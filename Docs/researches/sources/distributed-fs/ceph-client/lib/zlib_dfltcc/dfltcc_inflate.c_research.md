# sources/distributed-fs/ceph-client/lib/zlib_dfltcc/dfltcc_inflate.c

Purpose: Implements the DFLTCC-backed inflate hook for s390, allowing hardware expansion to run from the generic inflate state machine at block boundaries.

Important APIs/functions:
- `dfltcc_can_inflate()` checks command-line support mode and hardware XPND/FMT0 availability.
- `dfltcc_reset_inflate_state()` resets common DFLTCC state.
- `dfltcc_inflate()` performs the hardware expand operation or asks the generic inflate state machine to continue in software.
- Internal `dfltcc_inflate_disable()` disables future hardware use if still safe, or fails if hardware already emitted output and software cannot resume.
- Internal `dfltcc_xpnd()` wraps `DFLTCC_XPND | HBT_CIRCULAR` and updates stream pointers/availability.

Control flow:
- The generic `inflate.c` invokes this hook from `TYPEDO` before software block decoding.
- `Z_BLOCK` and `Z_PACKET_FLUSH` are unsupported by DFLTCC. If hardware has not been used, the hook disables availability and returns software fallback; otherwise it returns stream error.
- If the stream is at the last block, it moves to `CHECK`.
- For normal hardware inflate, the hook maps bit accumulator/checksum/history into the parameter block, loops while hardware reports AGAIN, maps output state back, and returns CONTINUE or BREAK based on operand exhaustion.
- Corrupt operand with OESC sets inflate mode BAD for generic error handling.

State and persistence:
- Uses the common `struct dfltcc_state` adjacent to `inflate_state`. `param->nt`, `param->cf`, `param->hl`, `param->sbb`, and `param->cv` preserve hardware continuation and checksum state.
- Hardware writes into the generic inflate sliding window, which must exist and be nonzero.

Dependencies and integration:
- Includes `../zlib_inflate/inflate.h`, `dfltcc_util.h`, `dfltcc_inflate.h`, s390 setup, and `<linux/zutil.h>`.
- Exported functions are available to module users/tests.

Risks:
- Once hardware has consumed data, software fallback may not have enough internal decode state to continue; this is explicitly guarded.
- The hook must preserve `state->bits`, `last`, `check`, and mode transitions exactly or the generic trailer/check path will misbehave.
- If no window is available, the code moves to `MEM`; workspace setup must keep the DFLTCC-aligned window valid.

Test signals:
- s390 inflate tests with DFLTCC enabled/disabled and deflate-only/inflate-only boot modes.
- Streams using `Z_BLOCK` and `Z_PACKET_FLUSH` before and after hardware use.
- Corrupt deflate streams with hardware OESC reporting.
- Tiny buffers and continuation-flag paths.
