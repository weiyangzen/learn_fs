<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/rescomm.private.h -->
# sources/distributed-fs/coda/coda-src/resolution/rescomm.private.h

Purpose: private compatibility helpers for resolution communication synchronization and string normalization.

Important APIs: declares `ResProcWait(char *)` and `ResProcSignal(char *, int)`, then maps condition macros (`CONDITION_INIT`, `CONDITION_WAIT`, `CONDITION_SIGNAL`) onto LWP wait/signal functions. `TRANSLATE_TO_LOWER` lowercases a mutable C string in place.

State/persistence: no persistent state. Synchronization state is external to LWP wait addresses supplied by callers.

Dependencies/integration: included by `rescomm.cc`; assumes C linkage and C library `isupper`/`tolower` availability through the including file.

Risks/test signals: macros evaluate raw pointer addresses as condition keys and provide no mutex semantics. `TRANSLATE_TO_LOWER` passes `char` directly to ctype macros, which can be undefined for negative signed chars. Test server-name normalization with mixed case and non-ASCII bytes only if such names are expected; otherwise keep hostnames ASCII.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/rescomm.private.h -->
