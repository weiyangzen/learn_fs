# sources/cloud-native/ostree/src/libostree/ostree-repo-deprecated.h

## Purpose
This header preserves deprecated checkout API declarations and compatibility types for older libostree consumers. It defines the legacy `OstreeRepoCheckoutOptions` structure and declares `ostree_repo_checkout_tree_at()` as deprecated in favor of `ostree_repo_checkout_at()`.

## Important APIs, Types, And Functions
The central type is `OstreeRepoCheckoutOptions`, which carries checkout mode, overwrite mode, boolean bitfields for uncompressed cache, fsync disabling, whiteout processing, no-copy fallback, a `subpath`, a devino cache pointer, and reserved fields for ABI stability. The only function declaration is `_OSTREE_PUBLIC gboolean ostree_repo_checkout_tree_at(...) G_GNUC_DEPRECATED_FOR(ostree_repo_checkout_at)`.

## Control Flow
There is no executable control flow. The header contributes compile-time declarations, deprecation annotations, and scanner/deprecation macro compatibility for environments where `G_GNUC_DEPRECATED_FOR` may not be defined outside GI scanner processing.

## State And Persistence
The options struct carries transient checkout settings only. The reserved integer and pointer arrays are ABI padding so future or historical structure layout constraints do not break callers.

## Dependencies And Integration Points
It includes `ostree-core.h` and `ostree-types.h`, uses GLib declaration macros, and integrates with old callers that still invoke `ostree_repo_checkout_tree_at()` or allocate `OstreeRepoCheckoutOptions`. The `devino_to_csum_cache` field connects deprecated checkout flows with commit hardlink optimization used by repo commit code.

## Risks And Edge Cases
The major risk is ABI compatibility: field order, bitfield sizes, and reserved padding must not be casually changed. Because callers are expected to zero the struct before use, any additions would need to preserve zero-as-default behavior. Documentation says `ostree_repo_checkout_tree_at()` is superseded; new code should avoid this API.

## Test Signals
Useful signals are ABI/API compatibility checks, GI scanner behavior, compiler deprecation warnings, and build coverage for downstream code still including this header. Runtime behavior belongs to the checkout implementation, not this header.
