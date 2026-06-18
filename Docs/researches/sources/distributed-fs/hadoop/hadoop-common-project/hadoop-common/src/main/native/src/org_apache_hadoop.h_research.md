# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org_apache_hadoop.h

## Purpose
`org_apache_hadoop.h` is a shared native compatibility header for Hadoop JNI code. It supplies exception macros, dynamic-symbol loading helpers, platform-specific type/configuration glue, branch prediction fallbacks, class locking helpers, and retry-on-EINTR behavior.

## Important APIs, types, and functions
Key macros are `THROW`, `PASS_EXCEPTIONS`, `PASS_EXCEPTIONS_GOTO`, `PASS_EXCEPTIONS_RET`, `LOCK_CLASS`, `UNLOCK_CLASS`, and `RETRY_ON_EINTR`. Unix code gets `LOAD_DYNAMIC_SYMBOL` around `dlopen`/`dlsym`; Windows code defines Unicode settings, Windows headers, `do_dlsym`, and a Windows-specific `LOAD_DYNAMIC_SYMBOL`. `terror` creates formatted errors from `errno`.

## Control flow
Most constructs are macros that short-circuit on Java exceptions or retry interrupted syscalls. `LOAD_DYNAMIC_SYMBOL` attempts symbol resolution and throws Java exceptions on failure. `LOCK_CLASS` and `UNLOCK_CLASS` enter/exit Java monitor locks and propagate exceptions.

## State and persistence
The header has no own persistent state. It governs control-flow conventions and error propagation in many native translation units.

## Dependencies and integration points
It includes JNI and Hadoop config headers, and platform headers for Unix dynamic loading or Windows APIs. It is included by native security, checksum, loader, and YARN Windows executor code.

## Risks and test signals
Risks include macro side effects, inconsistent exception class names, monitor leaks if `UNLOCK_CLASS` is skipped, Windows macro substitutions such as `snprintf`, and divergence between this header's branch macros and `gcc_optimizations.h`. Test signals include native compilation on Unix and Windows, dynamic library load failure tests, JNI exception propagation tests, and EINTR retry coverage.
