# sources/cloud-native/ostree/src/libostree/ostree-version.h.in

## Purpose
Meson/configure template for generated libostree compile-time version macros and configured feature strings.

## Important APIs, Types, And Functions
Defines `OSTREE_YEAR_VERSION`, `OSTREE_RELEASE_VERSION`, `OSTREE_VERSION`, `OSTREE_VERSION_S`, `OSTREE_ENCODE_VERSION(year, release)`, `OSTREE_VERSION_HEX`, `OSTREE_CHECK_VERSION(year, release)`, and `OSTREE_BUILT_FEATURES`.

## Control Flow
No runtime control flow. Build substitution fills `@YEAR_VERSION@`, `@RELEASE_VERSION@`, `@VERSION@`, and `@OSTREE_FEATURES@`. Consumers use the macros in preprocessor or compile-time comparisons.

## State And Persistence Behavior
No runtime state. It records build-time version and feature information into installed headers, affecting downstream conditional compilation and diagnostics.

## Dependencies And Integration Points
Integrated with the build system and public libostree headers. `OSTREE_BUILT_FEATURES` is hidden from GI scanner to avoid introspection issues with a free-form feature string.

## Risks
Incorrect substitution breaks public version reporting and downstream `OSTREE_CHECK_VERSION` guards. Year/release encoding assumes values fit in the bit packing used by `OSTREE_ENCODE_VERSION`.

## Test Signals
Build-system tests, installed-header compile tests, and checks that `ostree --version`/library headers agree on features and version are useful signals.
