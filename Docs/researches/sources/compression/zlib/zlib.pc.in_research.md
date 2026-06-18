# sources/compression/zlib/zlib.pc.in

`zlib.pc.in` is the pkg-config template for zlib. Configure substitutes install paths and version into fields consumed by downstream build systems.

Important variables are `prefix`, `exec_prefix`, `libdir`, `sharedlibdir`, `includedir`, and `@VERSION@`. It emits package metadata (`Name`, `Description`, `Version`, `License`), an empty `Requires`, `Libs: -L${libdir} -L${sharedlibdir} -lz`, and `Cflags: -I${includedir}`.

There is no executable control flow or runtime state. The generated `.pc` file persists in the install tree and drives downstream compiler/linker flags. Integration overlaps with CMake package config and traditional install metadata. Risks are bad path/version substitution, duplicated or misordered library directories, and metadata drift from `zlib.h`. Test signals are `pkg-config --cflags --libs zlib` producing valid paths and a downstream compile/link smoke test reporting the expected `zlibVersion()`.
