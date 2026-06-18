# sources/distributed-fs/glusterfs/xlators/features/read-only/src/Makefile.am

## Purpose
This automake file builds the read-only and WORM feature translator modules.

## Important APIs and Build Targets
- `xlator_LTLIBRARIES = read-only.la worm.la` builds two loadable xlator modules.
- `xlatordir` installs them under the GlusterFS feature xlator directory.
- `noinst_HEADERS` includes `read-only.h`, `read-only-mem-types.h`, `read-only-common.h`, and `worm-helper.h`.
- `read_only_la_SOURCES = read-only.c read-only-common.c`.
- `worm_la_SOURCES = read-only-common.c worm-helper.c worm.c`.
- Both modules link against `libglusterfs.la`.
- `AM_CPPFLAGS` adds libglusterfs and RPC XDR include paths; `AM_CFLAGS` uses `-Wall` and GlusterFS C flags.

## Control Flow
There is no runtime flow; it determines which code is compiled into each translator. The shared `read-only-common.c` is intentionally compiled into both modules.

## State and Persistence
No runtime state is stored here. Build outputs are libtool modules installed in the GlusterFS xlator tree.

## Dependencies and Integration Points
Depends on the top-level build system variables `GF_XLATOR_DEFAULT_LDFLAGS`, `GF_CPPFLAGS`, and `GF_CFLAGS`, plus `libglusterfs`. The WORM module depends on helper symbols from `worm-helper.c`; the read-only module does not.

## Risks
Adding a helper used by both modules requires updating the correct source list. Missing a header from `noinst_HEADERS` can break distribution packaging. Since `read-only-common.c` is compiled into both modules, any global symbols there must remain compatible with both.

## Test Signals
Build should produce `read-only.la` and `worm.la`; link failures indicate source/header dependency drift. Packaging tests should confirm both modules install in `xlator/features`.
