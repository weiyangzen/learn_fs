# sources/cloud-native/ostree/src/libostree/ostree-deployment.h

## Purpose
This public header declares the `OstreeDeployment` type and stable API for inspecting and lightly mutating deployments in a sysroot.

## Important APIs, Types, And Functions
It defines GType/check macros, `OSTREE_ORIGIN_TRANSIENT_GROUP`, the opaque `OstreeDeployment`, constructors, hash/equality helpers, getters for index/osname/checksums/serials/bootconfig/origin, state queries for staged/finalization-locked/soft-reboot/pinned, setters for index/bootserial/bootconfig/origin, transient origin cleanup, clone, origin relpath, and `OstreeDeploymentUnlockedState` with string conversion.

## Control Flow, State, And Persistence
The header’s public contract maps deployment identity to persistent sysroot layout. The origin transient group documents state that should not be carried across upgrades, while `.origin` relpaths are derived from deployment identity.

## Dependencies And Integration Points
It depends on `ostree-bootconfig-parser.h` and `ostree-types.h`. It is consumed by admin, sysroot, upgrader, bootloader, and bindings code.

## Risks And Test Signals
Public API additions must preserve ABI. State-query semantics evolve with features such as staged deployments and soft reboot, so tests should verify behavior with older origin/bootconfig data. Binding/introspection tests should confirm transfer annotations, nullability, and enum stability.
