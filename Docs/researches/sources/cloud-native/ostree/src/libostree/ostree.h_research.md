# sources/cloud-native/ostree/src/libostree/ostree.h

## Purpose
Primary public umbrella header for libostree consumers.

## Important APIs, Types, And Functions
It includes public headers for async progress, bootconfig parsing, content writing, core objects, deployments, diffs, GPG verify results, kernel args, mutable trees, refs, remotes, repo files, repo finders, repo OS APIs, repo APIs, signing, sysroot upgrader, sysroot APIs, version macros, and autocleanup support.

## Control Flow
No runtime control flow. Inclusion order matters: `ostree-autocleanups.h` is included after type definitions.

## State And Persistence Behavior
No state is stored. It exposes the full public API surface for repository and sysroot persistence operations implemented elsewhere.

## Dependencies And Integration Points
Downstream applications include this header to access libostree. It coordinates installed header layout and depends on all referenced public headers being available and self-consistent.

## Risks
Adding/removing includes changes what downstream code can compile with a single include. Include ordering can affect autocleanup declarations and opaque type visibility.

## Test Signals
Installed-header compile tests, GI scanner runs, and downstream sample builds are the relevant signals.
