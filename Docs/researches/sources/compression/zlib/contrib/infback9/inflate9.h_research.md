# sources/compression/zlib/contrib/infback9/inflate9.h

Purpose: defines the internal state machine modes and state structure for deflate64 callback inflation.

Important APIs/types/functions: enum `inflate_mode` with `TYPE`, `STORED`, `TABLE`, `LEN`, `DONE`, and `BAD`; `struct inflate_state` with `window`, dynamic code counts, `next`, `lens[320]`, `work[288]`, and `codes[ENOUGH]`.

Control flow: `infback9.c` uses `inflate_mode` to drive block parsing and code decoding. The dynamic-table fields are populated while reading a dynamic block and then passed to `inflate_table9()` to build decode tables in `codes`.

State and persistence: one `inflate_state` is allocated per zlib stream by `inflateBack9Init_`. The window pointer persists, while dynamic-table arrays are reused per block.

Dependencies/integration: depends on `code` and `ENOUGH` from `inftree9.h`, zlib `FAR`, and the layout expectations of `infback9.c`.

Risks: this is internal API and not guarded by an include guard in the visible snippet, so include ordering matters. Array sizes are deflate64-specific and must match the maximum symbol counts used by `infback9.c`.

Test signals: compile coverage validates field availability; runtime dynamic-block tests validate the sizing and mode transitions.
