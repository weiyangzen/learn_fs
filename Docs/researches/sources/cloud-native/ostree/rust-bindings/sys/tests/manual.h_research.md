# sources/cloud-native/ostree/rust-bindings/sys/tests/manual.h

Purpose: This hand-maintained C header supports generated ABI fixtures by including libostree headers and defining compatibility constants for older libostree versions.

Important APIs, types, and functions: It includes `<ostree.h>`. If `OSTREE_CHECK_VERSION(2019, 2)` is false, it defines `OSTREE_REPO_LIST_REFS_EXT_EXCLUDE_MIRRORS`, `OSTREE_REPO_REMOTE_CHANGE_REPLACE`, and `OSTREE_REPO_RESOLVE_REV_EXT_LOCAL_ONLY` to their expected numeric values.

Control flow: Preprocessor-only control flow checks the libostree version and conditionally defines missing constants before C fixtures are compiled.

State and persistence behavior: None.

Dependencies and integration points: Used by `constant.c` and `layout.c`. It is C-side counterpart to `sys/src/manual.rs`: both patch generated or version-dependent ABI knowledge.

Risks: Backfilled values must match the newer libostree ABI exactly. Incorrect fallback values would make ABI tests pass for the wrong Rust constant and could mislead compatibility claims.

Test signals: Successful compilation of the C fixtures against libostree versions older than 2019.2 indicates these fallbacks cover the expected missing constants.
