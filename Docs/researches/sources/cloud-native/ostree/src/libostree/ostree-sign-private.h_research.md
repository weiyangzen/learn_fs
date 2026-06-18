# sources/cloud-native/ostree/src/libostree/ostree-sign-private.h

Purpose: private declaration for signing summary files at an arbitrary directory fd, separating internal repo metadata signing support from the public `ostree_sign_summary` convenience API.

Important APIs/types/functions: `_ostree_sign_summary_at` signs `summary` and writes `summary.sig` in `dir_fd` using an `OstreeSign` engine, an `OstreeRepo`, and a variant array of secret keys.

Control flow: internal callers pass a directory fd; the implementation reads existing `summary`/`summary.sig`, signs summary data for each key, appends signatures to metadata, normalizes the variant, and replaces `summary.sig`.

State/persistence: persists `summary.sig` in the selected directory. Does not own key storage beyond temporarily setting keys on the backend while signing.

Dependencies/integration: depends on `ostree-sign.h` and `ostree-types.h`. Used by `ostree-sign.c`; useful for fd-relative repository summary contexts.

Risks: private API has no ABI guarantee. Callers must ensure `dir_fd` points at the intended repository-like directory and contains `summary`.

Test signals: summary signature tests exercise the public path that delegates to this helper.
