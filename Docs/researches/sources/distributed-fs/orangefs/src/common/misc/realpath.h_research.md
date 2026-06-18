# sources/distributed-fs/orangefs/src/common/misc/realpath.h

Purpose: Declares the OrangeFS internal `PINT_realpath` canonicalization routine implemented in `realpath.c`.

Important APIs and types: `int PINT_realpath(const char *path, char *resolved_path, int m);` takes an input path, caller-provided output buffer, and maximum output length, returning `0` or a negative PVFS error.

Control flow: No runtime logic. The header exposes a libc-like realpath contract to path-resolution code while allowing the implementation to differ between POSIX and Windows builds.

State and persistence: None. Callers own all buffers.

Dependencies and integration points: Included by `pvfs2-util.c`, `pvfs2-win-util.c`, and the implementation file. The declaration intentionally avoids pulling in large dependency headers, but callers must know PVFS error-code semantics.

Risks: The third parameter is named only `m`, which obscures expected units and relation to `resolved_path` length. There is no include guard, so repeated inclusion relies on identical declaration tolerance. No nullability or buffer-size annotations are present.

Test signals: Compile repeated includes, verify declaration matches implementation on POSIX and Windows, and exercise caller behavior for `NULL` pointers and undersized buffers.
