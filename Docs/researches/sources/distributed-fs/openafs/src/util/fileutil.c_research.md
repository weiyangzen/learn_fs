# sources/distributed-fs/openafs/src/util/fileutil.c

Purpose: Provides low-level file path normalization and buffered file-descriptor reading without using `FILE *`, preserving compatibility with historical fileserver limitations and Windows CRT differences.

Important APIs: `FilepathNormalizeEx(char *path, int slashType)` rewrites slashes, collapses repeated separators, and removes a trailing separator except root/drive-root cases. `FilepathNormalize()` selects forward slashes. `BufioOpen()`, `BufioGets()`, and `BufioClose()` implement a small buffered line reader over `open`/`read`/`close` or `_open`/`_read`/`_close`.

Control flow and state: `BufioOpen()` allocates a `bufio_t`, opens the file, and initializes `pos`, `len`, and `eof`. `BufioGets()` refills the 4096-byte buffer as needed, copies until newline or caller buffer limit, null terminates, and returns length or `-1` for EOF/error. It does not strip carriage returns despite the comment saying so; it only terminates at `\n`.

Dependencies and integration: Includes `fileutil.h`, roken, `afs/stds.h`, and `errmap_nt.h` on Windows. `dirpath.c`, host temp-dir logic, and config readers depend on normalized slash conventions.

Risks and test signals: `FilepathNormalizeEx()` decrements `pP` even for an empty string, which can underflow before comparing; callers should avoid empty mutable strings. `BufioGets()` truncates long lines without signaling that truncation occurred. Direct tests are not present here, but path normalization is exercised by `dirpath_test`.
