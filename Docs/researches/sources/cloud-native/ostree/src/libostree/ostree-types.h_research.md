# sources/cloud-native/ostree/src/libostree/ostree-types.h

## Purpose
Central forward-declaration header for libostree public and semi-public object types, avoiding include cycles across the large API surface.

## Important APIs, Types, And Functions
It defines `_OSTREE_PUBLIC` as `extern` when not already provided and forward declares `OstreeRepo`, `OstreeRepoDevInoCache`, `OstreeSePolicy`, `OstreeSysroot`, `OstreeSysrootUpgrader`, `OstreeMutableTree`, `OstreeRepoFile`, `_OstreeContentWriter`, `OstreeRemote`, and `_OstreeKernelArgs`.

## Control Flow
There is no runtime control flow. The file is included by headers needing pointer types without full definitions.

## State And Persistence Behavior
No state is stored. Its role is compile-time type sharing.

## Dependencies And Integration Points
Depends only on GIO and GLib declarations. It is a foundational integration header for libostree public headers, introspection, and consumers compiling against opaque object pointers.

## Risks
Changing typedef names or `_OSTREE_PUBLIC` handling can break ABI headers and generated bindings. Forward declarations must match real struct tags exactly.

## Test Signals
Compile coverage across public headers, introspection generation, and downstream build tests are the primary signals.
