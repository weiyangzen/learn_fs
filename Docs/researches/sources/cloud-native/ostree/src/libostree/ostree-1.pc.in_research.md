# sources/cloud-native/ostree/src/libostree/ostree-1.pc.in

Purpose: This pkg-config template describes how external C/Rust build systems discover libostree compiler and linker flags.

Important APIs, types, and functions: It defines substituted variables `prefix`, `exec_prefix`, `libdir`, `includedir`, `features`, and `cliextdir`. Metadata includes `Name: OSTree`, description, version, public requirement `gio-unix-2.0`, private requirements/libs substitutions, `Libs: -L${libdir} -lostree-1`, and `Cflags: -I${includedir}/ostree-1`.

Control flow: Meson/configure-time substitution produces the final `.pc` file; pkg-config later reads the static fields.

State and persistence behavior: Installed development metadata persists on the system and directly affects downstream compilation. It does not execute code.

Dependencies and integration points: Used by `pkg-config --cflags ostree-1` in `sys/tests/abi.rs`, by downstream C projects, and by Rust build scripts or tests needing libostree headers.

Risks: Missing public/private dependencies or wrong include/lib paths break downstream builds. Incorrect `features` can mislead feature detection. Public vs private dependency placement affects static linking.

Test signals: ABI tests in this subset use pkg-config cflags, so their successful compilation indirectly validates the installed `.pc` metadata.
