# sources/cloud-native/ostree/src/libostree/ostree-gpg-verifier.h

## Purpose
This private header declares the `OstreeGpgVerifier` GObject and its key-loading/signature-verification API.

## Important APIs, Types, And Functions
It defines type macros, an opaque `OstreeGpgVerifier`, autoptr cleanup, `_ostree_gpg_verifier_new()`, `_ostree_gpg_verifier_check_signature()`, `_ostree_gpg_verifier_list_keys()`, keyring dir/file/data adders, global keyring import, ASCII key adders, and keyfile path/dir adders.

## Control Flow, State, And Persistence
The header defines verifier ownership contracts: key inputs are accumulated on the verifier object, and signature checks return an `OstreeGpgVerifyResult` tied to verifier-imported temporary key state.

## Dependencies And Integration Points
It includes `ostree-gpg-verify-result.h` and is used by repository verification internals, not public GI consumers.

## Risks And Test Signals
Because this is private but security-critical, tests should verify all declared import paths feed equivalent trust state and that errors are surfaced through `GError`. Header/API parity with `ostree-gpg-verifier.c` should be covered by build tests across GPG-enabled configurations.
