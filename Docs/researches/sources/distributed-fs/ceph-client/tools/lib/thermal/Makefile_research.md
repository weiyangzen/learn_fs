# sources/distributed-fs/ceph-client/tools/lib/thermal/Makefile

Purpose: Builds, links, installs, and cleans the `libthermal` static and shared libraries plus pkg-config metadata and headers.

Important APIs/types/functions: Version variables define `0.0.1`. Targets include `libs`, `all`, `clean`, `install_lib`, `install_headers`, `install_pkgconfig`, `install_doc`, and `install`. Artifacts include `libthermal.a`, `libthermal.so.$(VERSION)`, symlinks, and `libthermal.pc`.

Control flow: Resolves `srctree`, computes libdir, gets libnl CFLAGS from `pkg-config` or fallback path, creates a symlink to the thermal UAPI header, builds `libthermal-in.o`, archives static lib, links shared lib with a version script, generates pkg-config file from a template, and installs artifacts.

State and persistence: Produces static/shared libraries, symlinks, pkg-config file, and a tools UAPI symlink. Install copies artifacts into DESTDIR/prefix. Clean removes build products and the symlink.

Dependencies/integration: Depends on kernel tools build system, libnl-3.0 headers/libraries, `include/uapi/linux/thermal.h`, and `libthermal.map`/pc template files. Includes many kernel tools include directories.

Risks: Variables `CFGLAS` appear to be misspelled and likely intended as linker flags, so the `-L.`/`-lthermal` additions may be unused. `-Werror` is forced, making builds sensitive to external libnl/compiler warnings. Header symlink target assumes source-tree layout. Shared link command relies on external linker defaults for libnl linkage.

Test signals: Build static/shared libs with and without pkg-config libnl cflags, custom `OUTPUT`, DESTDIR install, clean, and packaging validation of `.pc` and symlinks.
