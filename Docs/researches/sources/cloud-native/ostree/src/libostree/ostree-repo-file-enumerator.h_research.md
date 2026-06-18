# sources/cloud-native/ostree/src/libostree/ostree-repo-file-enumerator.h

## Purpose
This private header declares the `OstreeRepoFileEnumerator` GObject type and constructor used to enumerate children of `OstreeRepoFile` directories.

## Important APIs, Types, And Functions
It defines type macros for `OSTREE_TYPE_REPO_FILE_ENUMERATOR`, cast/check/get-class helpers, forward declarations for `OstreeRepoFileEnumerator` and its class, a class struct derived from `GFileEnumeratorClass`, `_ostree_repo_file_enumerator_get_type()`, and `_ostree_repo_file_enumerator_new()`.

## Control Flow
There is no runtime control flow in the header. It provides declarations consumed by `ostree-repo-file-enumerator.c` and `ostree-repo-file.c`.

## State And Persistence
No persistent state is defined here. The declared class is private/internal and carries instance state only in the C file.

## Dependencies And Integration Points
The header includes `ostree-repo-file.h`, which provides the `OstreeRepoFile` type accepted by the constructor. It integrates with the `GFile` interface implementation for committed OSTree trees.

## Risks And Edge Cases
Because this is an internal header, ABI risk is lower than public headers, but type macro consistency and constructor signature must match the implementation. Any change to the constructor affects `ostree_repo_file_enumerate_children()`.

## Test Signals
Build and type-registration tests are the main direct signals. Indirect coverage comes from `GFile` enumeration tests on `OstreeRepoFile`.
