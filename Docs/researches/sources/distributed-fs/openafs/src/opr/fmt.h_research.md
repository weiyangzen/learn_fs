# sources/distributed-fs/openafs/src/opr/fmt.h

Purpose: public interface for the OPR callback formatter.

Important APIs/types/functions: forward-declares `opr_fmt_ctx_priv` and `opr_fmt_ctx`, defines `opr_fmtr` callback type, and defines `struct opr_fmt_ctx_s` with formatter table, user data, output callback, and private implementation pointer. Declares `opr_fmt`.

Control flow: no runtime logic. Callback users write output through `ctx->put`.

State and persistence: no header-owned state.

Dependencies/integration: depends on `va_list` being visible to includers. Installed as `opr/fmt.h`.

Risks and test signals: the formatter table must have 256 entries indexed by unsigned char values. Callback implementations must not assume `priv` layout. Compile-time integration tests catch missing `stdarg.h` context.
