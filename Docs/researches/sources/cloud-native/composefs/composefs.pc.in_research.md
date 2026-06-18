# sources/cloud-native/composefs/composefs.pc.in

Purpose: pkg-config template for libcomposefs consumers.

Important APIs/types/functions: variables `prefix`, `exec_prefix`, `libdir`, `includedir`; fields `Name`, `Description`, `Version`, `Requires`, `Requires.private`, `Libs`, `Libs.private`, and `Cflags`.

Control flow: Meson/configure substitutes placeholders and installs the `.pc` file for downstream builds.

State/persistence: installed metadata under pkgconfig directory.

Dependencies/integration: integrates with package builds, RPM spec, and downstream C consumers linking `-lcomposefs`.

Risks/test signals: incorrect public/private dependency placement can overlink or underlink consumers. Build/install CI validates template substitution.
