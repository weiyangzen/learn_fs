# sources/distributed-fs/ceph-client/scripts/ssl-common.h

Purpose: `ssl-common.h` provides shared OpenSSL error-draining and error-checking helpers for signing/certificate host tools such as `sign-file` and `extract-cert`.

Important APIs, types, and functions: `drain_openssl_errors(int l, int silent)` prints and clears pending OpenSSL errors, optionally with a source line banner. `ERR(cond, fmt, ...)` drains OpenSSL errors, evaluates a condition, and calls `errx(1, ...)` on failure.

Control flow: callers use `ERR()` after OpenSSL calls so queued library errors do not accumulate and so failures include OpenSSL diagnostics.

State and persistence: it mutates OpenSSL's per-thread error queue by consuming errors. No file state.

Dependencies and integration points: requires OpenSSL error APIs, stdio, err, and bool definitions from including files. `sign-file.c` includes it after OpenSSL headers.

Risks: the printed banner says `main.c` regardless of actual source file, which can confuse diagnostics. `ERR()` drains errors even when the condition is false, which is intentional cleanup but may hide warnings from later code.

Test signals: inject OpenSSL failures in sign-file/extract-cert paths and verify useful diagnostics and nonzero exits.
