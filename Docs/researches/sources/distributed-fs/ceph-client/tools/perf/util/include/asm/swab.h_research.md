# sources/distributed-fs/ceph-client/tools/perf/util/include/asm/swab.h

Purpose: placeholder `asm/swab.h` for the perf tools include tree. It satisfies include paths that expect an architecture byte-swap header.

Important APIs and types: none; the file contains only `/* stub */`.

Control flow: none.

State and persistence: none.

Dependencies and integration: relies on other userspace or Linux helper headers to provide actual byte-swap APIs. This file's integration role is include compatibility, not functionality.

Risks: future code that expects architecture-specific swab definitions from this header would silently get nothing. Keep real byte-order behavior in explicit endian/byteswap headers.

Test signals: build coverage for source files that include kernel-like `asm/swab.h` through perf's compatibility include path.
