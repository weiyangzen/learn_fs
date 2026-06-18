# sources/distributed-fs/ceph-client/tools/objtool/include/objtool/util.h

Purpose: Provides a checked `snprintf` wrapper macro used when constructing bounded ELF section and symbol names.

Important APIs/types/functions: `_UTIL_H`, `snprintf_check`.

Control flow: The macro calls `snprintf`, reports truncation through `ERROR`, and returns `-1` from the caller on overflow.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on objtool warning macros and standard snprintf semantics.

Risks: It assumes use inside functions returning integer status; misuse in other return contexts will be wrong.

Test signals: Boundary-length KLP symbol/section names and normal short names.

Source coverage: researched from the complete local file (20 lines, 448 bytes).
