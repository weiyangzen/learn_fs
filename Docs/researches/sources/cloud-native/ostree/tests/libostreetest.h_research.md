<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/libostreetest.h -->
## sources/cloud-native/ostree/tests/libostreetest.h

Purpose: public C header for the libostreetest helper functions.

Important APIs/functions: declares shell bridge, tmpdir template, repo setup, relabel/xattr probes, and sysroot setup. Uses `G_BEGIN_DECLS/G_END_DECLS` for C++ compatibility and includes `gio/gio.h` plus `ostree.h`.

Control flow/state: no implementation or state; it defines the API contract consumed by C tests.

Dependencies/integration: must stay in sync with `libostreetest.c` and linked test binaries.

Risks/test signals: signature drift breaks compilation. The header exposes nullable/error-bearing GLib patterns via `GError **` and object return pointers.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/libostreetest.h -->
