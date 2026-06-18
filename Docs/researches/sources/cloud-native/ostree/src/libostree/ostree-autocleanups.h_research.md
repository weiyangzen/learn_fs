<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-autocleanups.h -->
# sources/cloud-native/ostree/src/libostree/ostree-autocleanups.h

## Purpose
Defines GLib `g_autoptr`, `g_auto`, and `g_autofree` cleanup hooks for exported OSTree types when building libostree or when the consuming GLib is new enough to expose cleanup support. It lets callers use automatic stack cleanup for common libostree objects without hand-written `goto out` cleanup blocks.

## Important APIs and Types
The file declares cleanup functions for refcounted objects such as `OstreeAsyncProgress`, `OstreeBootconfigParser`, `OstreeDeployment`, `OstreeMutableTree`, `OstreeRepo`, `OstreeRepoFile`, `OstreeSePolicy`, `OstreeSysroot`, and `OstreeSysrootUpgrader`, plus boxed/manual types such as `OstreeDiffItem`, `OstreeRepoCommitModifier`, `OstreeRepoDevInoCache`, `OstreeCommitSizesEntry`, `OstreeKernelArgs`, `OstreeCollectionRef`, `OstreeRemote`, and `OstreeRepoFinderResult`. It also defines clear/free cleanup for `OstreeRepoCommitTraverseIter`, `OstreeCollectionRefv`, and `OstreeRepoFinderResultv`.

## Control Flow
There is no runtime control flow. The only branch is a preprocessor guard: cleanup macros are exposed during `OSTREE_COMPILATION` or for GLib 2.44 and newer.

## State and Persistence
No state is stored. The cleanup hooks affect ownership discipline at call sites and prevent leaks during early returns.

## Dependencies and Integration Points
Includes `<ostree.h>` and depends on each type's corresponding free, unref, or clear function. It is included by public and internal libostree code that wants GLib automatic cleanup syntax.

## Risks
The guard avoids exporting libglnx cleanup backports to old-GLib consumers, which is important ABI/API hygiene. Adding a type here requires choosing the exact matching destructor; a wrong cleanup function can cause leaks, double frees, or missed finalization.

## Test Signals
Compile tests with supported minimum GLib and modern GLib are the main signal. Leak-checking code paths that use `g_autoptr(OstreeRepo)` and related cleanup declarations verifies destructor pairing.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-autocleanups.h -->
