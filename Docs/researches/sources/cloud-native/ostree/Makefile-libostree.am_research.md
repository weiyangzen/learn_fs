<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/Makefile-libostree.am -->
## sources/cloud-native/ostree/Makefile-libostree.am

### Purpose
This large automake fragment builds and installs the core `libostree-1.la` library plus helper `libbupsplit.la`, generated enum files, introspection artifacts, pkg-config metadata, and install hooks.

### APIs, Types, and Control Flow
It includes public header definitions, declares `libbupsplit.la`, installs public headers under `ostree-1`, generates `ostree-enumtypes.{h,c}` using `glib-mkenums`, and populates `libostree_1_la_SOURCES` with repository, sysroot, deployment, bootloader, static-delta, repo-finder, signing, blob-reader, compression, checksum, and utility sources. Conditional sections add libarchive, TLS cert interaction, Avahi, GPGME or dummy GPG result, curl/libsoup fetchers, libmount, SELinux, systemd, composefs, and introspection support. Link flags use a released symbol version script and hidden visibility with `_OSTREE_PUBLIC`.

### State, Dependencies, and Integration
Build artifacts include generated enum sources, GIR/typelib files, `ostree-1.pc`, and installed `trusted.gpg.d` README plus `/etc/ostree/remotes.d` creation through an install hook. It links against `libotutil`, `libotcore`, `libglnx`, `libbsdiff`, crypto, zlib, lzma, GLib/GIO, and optional feature libraries.

### Risks and Test Signals
Feature conditionals must stay consistent with `configure.ac`; adding sources without matching CFLAGS/LIBADD can break only certain distros. Symbol files are ABI gates. Test signals include full matrix builds, introspection builds, symbol tests, installed headers, and package linker checks.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/Makefile-libostree.am -->
