# sources/cloud-native/ostree/src/libostree/ostree-diff.h

## Purpose
This public header declares OSTree directory diff APIs and the boxed `OstreeDiffItem` result type.

## Important APIs, Types, And Functions
`OstreeDiffFlags` currently supports `OSTREE_DIFF_FLAGS_IGNORE_XATTRS`. `OstreeDiffItem` contains atomic refcount, source/target `GFile`s, source/target `GFileInfo`s, and optional checksums. Ref/unref and GType functions make it usable from GLib containers/bindings. `ostree_diff_dirs()` and `ostree_diff_dirs_with_options()` fill modified/removed/added arrays. `OstreeDiffDirsOptions` contains owner remap fields plus reserved booleans, ints, and pointers for ABI extension; `OSTREE_DIFF_DIRS_OPTIONS_INIT` sets UID/GID to `-1`. `ostree_diff_print()` emits a human-readable summary.

## Control Flow, State, And Persistence
The header defines caller ownership expectations: arrays are supplied by the caller and receive object references or owned diff items. No persistent state is created.

## Dependencies And Integration Points
It includes core and type headers and references `OstreeRepoDevInoCache`. It is consumed by C users, CLI code, and introspection-visible APIs.

## Risks And Test Signals
Because the options struct is ABI-extensible, initialization discipline matters. Tests should ensure callers using `OSTREE_DIFF_DIRS_OPTIONS_INIT` avoid uninitialized owner fields, boxed type ref/unref works, and introspection sees correct element types.
