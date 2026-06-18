# sources/cloud-native/ostree/configure.ac

Purpose: authoritative autotools configuration for libostree. It defines package versioning, compiler/tool checks, dependency discovery, optional feature flags, automake conditionals, generated files, and the final configure summary.

Important APIs/functions: `AC_INIT`, `AM_INIT_AUTOMAKE`, `AC_PROG_CC`, `AC_PROG_YACC`, `LT_INIT`, `PKG_CHECK_MODULES`, `AC_ARG_WITH`, `AC_ARG_ENABLE`, `AM_CONDITIONAL`, `AC_DEFINE`, `AC_SUBST`, `AC_CONFIG_FILES`, and `AC_OUTPUT`. Important outputs include `config.h`, `Makefile`, `apidoc/Makefile`, `src/libostree/ostree-1.pc`, and `src/libostree/ostree-version.h`.

Control flow: establishes version `2026.2`, compiler warning flags, sanitizer/thread-sanitizer conditionals, libtool, baseline OSTree feature strings, GLib/libglnx, platform functions, and pkg-config helpers. It then resolves core and optional dependencies: GLib/GIO, liblzma, zlib, e2p, curl, libsoup2/libsoup3, introspection, GPGME/gpg-error, composefs, libsodium, libarchive, SELinux, SMACK, OpenSSL/GnuTLS crypto, Avahi, libmount, FUSE/rofiles-fuse, dracut/mkinitcpio, systemd/libsystemd, GRUB behavior, static compiler, GJS tests, release/devel mode, and P2P. The final summary reports resolved feature state.

State and persistence: persists generated build configuration in `config.h`, makefiles, pkg-config metadata, and substituted headers. It accumulates `OSTREE_FEATURES`, `LIBS_PRIVATE`, `REQUIRES_PRIVATE`, and many `OT_DEP_*` variables that drive compilation and exported metadata.

Dependencies and integration: integrated by `autogen.sh`, CI build scripts, distribution packaging, documentation generation, man-page HTML generation, test selection, and C source build conditionals. Feature macros such as `HAVE_LIBSOUP3`, `HAVE_COMPOSEFS`, `HAVE_ED25519`, `BUILDOPT_SYSTEMD`, and `USE_OPENSSL` control compiled code paths.

Risks and test signals: risks include optional dependency defaults changing build surfaces, duplicate `gpgme` feature appends, `enable_otmpfile`/`enable_wrpseudo_compat` summary variables not shown in this file's visible checks, package-config version drift, and complex interaction between curl/soup test support. Test signals are `./configure` summaries across distro matrices, `make check`, `distcheck`, pkg-config correctness, and feature-specific tests for composefs, signatures, rofiles-fuse, SELinux, systemd, and docs.
