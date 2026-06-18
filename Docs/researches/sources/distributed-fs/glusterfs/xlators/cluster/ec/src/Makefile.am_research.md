# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/Makefile.am

## Purpose
Defines the Automake build for the EC/disperse translator module. It lists core EC sources/headers, conditionally adds CPU-specific dynamic code generators, sets include paths and libraries, and installs `disperse.so` as a symlink to `ec.so`.

## Important APIs and Variables
- `xlator_LTLIBRARIES = ec.la` and `xlatordir`: build/install the cluster xlator module.
- `ec_sources` / `ec_headers`: enumerate EC implementation files such as helpers, locks, read/write paths, method/galois/code layers, heal, and heald.
- `ENABLE_EC_DYNAMIC_INTEL`, `ENABLE_EC_DYNAMIC_X64`, `ENABLE_EC_DYNAMIC_SSE`, `ENABLE_EC_DYNAMIC_AVX`: configure-conditionals adding optimized generator files and headers.
- `ec_la_SOURCES`, `ec_la_LIBADD`, `ec_la_LDFLAGS`: module source list, libglusterfs dependency, and xlator module flags.
- `install-data-hook` / `uninstall-local`: maintain `disperse.so -> ec.so`.

## Control Flow
Build flow is declarative. Autotools expands conditionals based on configure results; if AVX support is enabled, `ec-code-avx.c` and `.h` are compiled into the module. Install creates a compatibility/alias symlink so the same implementation can be loaded as `disperse`.

## State and Persistence
Persistent outputs are build artifacts and installed module files/symlinks. No runtime state is defined here.

## Dependencies and Integration Points
Depends on libglusterfs, libxlator helper source/header, RPC/XDR include directories, generated builddir XDR headers, and configure variables such as `GF_CPPFLAGS`, `GF_CFLAGS`, `GF_XLATOR_DEFAULT_LDFLAGS`, and `GLUSTERFS_LIBEXECDIR`.

## Risks
- Conditional optimized sources must match configure CPU-feature checks; compiling AVX code without the right flags would fail or produce unusable code.
- The symlink hook assumes `ec.so` is the installed module name and destination directory exists.
- Source/header lists are manual, so new EC files must be added here.

## Test Signals
Build tests should verify EC builds with each dynamic-code conditional on/off, installation creates `disperse.so`, and uninstall removes it. Runtime EC tests indirectly validate that the selected optimized generator symbols are linked.
