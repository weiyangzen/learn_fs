# sources/distributed-fs/openafs/src/external/heimdal/krb5/expand_path.c

Purpose: expands `%{TOKEN}` path tokens for krb5 configuration paths across Unix and Windows.

Important APIs/types/functions: platform token expanders include `_expand_temp_folder()`, `_expand_bin_dir()`, `_expand_userid()`, `_expand_csidl()`, `_expand_path()`, `_expand_extra_token()`, and `_expand_null()`. The static `tokens[]` table maps names such as `LIBDIR`, `BINDIR`, `LIBEXEC`, `SBINDIR`, `TEMP`, `USERID`, `uid`, and `null`. Public internals are `_krb5_expand_path_tokens()` and `_krb5_expand_path_tokensv()`.

Control flow: `_krb5_expand_path_tokensv()` first copies variadic extra token pairs, then scans the input string for `%{`, appends literal spans or expanded token values, and reallocates the output buffer as it grows. `_expand_token()` checks syntax, searches caller-provided extra tokens first, then built-in tokens.

State and persistence behavior: no global mutable state. The returned path is heap-allocated and caller-owned. On Windows, output slashes are normalized to backslashes.

Dependencies and integration points: used by config file path handling when `KRB5_USE_PATH_TOKENS` is enabled. Unix paths use compile-time install directories and UID/TEMP helpers; Windows paths use CSIDL, token/SID APIs, module path lookup, and package directories.

Risks: token matching uses `strncmp()` against token length without checking exact built-in token length, so prefix ambiguities would matter if added. Varargs must be key/value pairs terminated by NULL. Setuid environment handling in Unix `_expand_temp_folder()` appears inverted and deserves scrutiny. Repeated reallocs are simple but potentially inefficient.

Test signals: literal-only paths, missing `}`, unknown token, extra token override, empty input, all built-in tokens, Windows slash conversion, and allocation-failure cleanup.
