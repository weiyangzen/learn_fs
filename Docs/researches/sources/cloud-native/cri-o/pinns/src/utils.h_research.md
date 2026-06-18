# sources/cloud-native/cri-o/pinns/src/utils.h

Purpose: shared C utility macros for `pinns`, covering EINTR retry, cleanup attributes, branch prediction, fd/file cleanup, and standardized warning/error output.

Important APIs/types/functions: `TEMP_FAILURE_RETRY`, `pexit`, `_pexit`, `pexitf`, `pwarn`, `pwarnf`, `nexit`, `nexitf`, `nwarn`, `nwarnf`, `_cleanup_`, `freep`, `closep`, `fclosep`, `_cleanup_free_`, `_cleanup_close_`, `_cleanup_fclose_`, `LIKELY`, and `UNLIKELY`.

Control flow: error macros print to stderr and either `exit` or `_exit`; cleanup functions are invoked by GCC/Clang cleanup attributes when variables go out of scope.

State and persistence: affects process exit behavior and closes/frees resources; no durable state.

Dependencies/integration: included by `pinns.c` and `sysctl.c`. Requires GNU-compatible compiler support for statement expressions and cleanup attributes.

Risks: macros with trailing semicolons on `nwarn`/`nwarnf` can be awkward in `if/else` contexts. Error macros exit immediately, so callers cannot recover. GNU extensions reduce portability outside the intended Linux toolchain.

Test signals: warning-free compile under the `pinns` Makefile's `-Werror -Wextra` settings is the main signal.
