# sources/distributed-fs/openafs/src/opr/fmt.c

Purpose: callback-driven percent-escape formatter with snprintf-like truncation semantics.

Important APIs/types/functions: `opr_fmt` is public. Internal `opr_fmt_ctx_priv_s` tracks input pointer, output pointer, remaining output bytes, and bytes written. `opr_fmt_cb` emits a character and counts it. `opr_fmt_internal` scans the format string and dispatches escape characters through a 256-entry formatter table.

Control flow: ordinary characters are copied. After `%`, the next byte indexes `ctx->fmtrs`; callbacks return 0 to finish escape processing, 1 to remain in escape mode, or -1 to abort. Unknown escapes emit the escape byte literally. The implementation always emits a terminating NUL during successful formatting and returns the number of bytes that would have been written excluding NUL.

State and persistence: state is stack-local per call and caller-provided output buffer. No global state.

Dependencies/integration: includes `fmt.h` and `afs/opr.h` for assertions. Used by code needing custom lightweight formatting.

Risks and test signals: if `n` is 0, the termination logic can write `out[-1]` when `ret >= n`; callers should pass positive sizes. Formatter callbacks consume a shared `va_list`, so callback conventions must match. Unit tests should cover truncation, unknown escapes, multi-step callbacks, and callback failure.
