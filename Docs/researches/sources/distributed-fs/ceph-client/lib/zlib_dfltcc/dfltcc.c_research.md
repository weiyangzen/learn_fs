# sources/distributed-fs/ceph-client/lib/zlib_dfltcc/dfltcc.c

Purpose: Provides common state reset and diagnostic formatting for System z DEFLATE CONVERSION CALL acceleration.

Important APIs/functions:
- `oesc_msg()` converts a nonzero Operation-Ending-Supplemental Code into `strm->msg` text, except in static/pre-boot builds.
- `dfltcc_reset_state()` queries available hardware functions when DFLTCC is enabled, copies the query result into `dfltcc_state->af`, clears the parameter block, and initializes task flags.

Control flow:
- On reset, `is_dfltcc_enabled()` gates a `DFLTCC_QAF` query. If disabled, available-functions state is zeroed so callers fall back to software.
- The parameter block is then cleared and initialized with `nt = 1` and `ribm = DFLTCC_RIBM`.

State and persistence:
- Updates only `struct dfltcc_state` embedded in each zlib stream workspace.
- No global mutable state here; global support mode comes from `zlib_dfltcc_support` in s390 setup code.

Dependencies and integration:
- Includes `dfltcc_util.h` and `dfltcc.h`.
- Called by deflate and inflate reset hooks.
- Module metadata declares GPL license.

Risks:
- The QAF call temporarily uses the parameter block storage and then copies out the available-function query; ordering matters.
- `sprintf()` writes into a fixed 64-byte `msg` buffer with a fixed format. Safe for current format but should not be expanded carelessly.

Test signals:
- Boot/run with `zlib_dfltcc_support` disabled and enabled to verify QAF behavior and fallback.
- Force nonzero OESC paths to confirm `strm->msg` propagation.
