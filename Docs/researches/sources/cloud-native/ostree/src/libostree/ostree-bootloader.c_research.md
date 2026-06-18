<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bootloader.c -->
# sources/cloud-native/ostree/src/libostree/ostree-bootloader.c

## Purpose
Defines the shared `OstreeBootloader` interface dispatch layer used by sysroot deployment code to operate on concrete bootloader backends uniformly.

## Important APIs and Types
`G_DEFINE_INTERFACE()` registers `OstreeBootloader`. Dispatch helpers are `_ostree_bootloader_query()`, `_ostree_bootloader_get_name()`, `_ostree_bootloader_write_config()`, `_ostree_bootloader_post_bls_sync()`, and `_ostree_bootloader_is_atomic()`.

## Control Flow
Each helper asserts the instance implements the interface and forwards to the relevant vfunc. `post_bls_sync` defaults to success if the backend omits the hook. `is_atomic` defaults to true if the backend omits the hook.

## State and Persistence
The interface layer stores no state. Concrete implementations own sysroot references and persistent bootloader files/stamps.

## Dependencies and Integration Points
Depends on `ostree-bootloader.h` and GObject. It is the integration point between sysroot deployment orchestration and GRUB2, syslinux, U-Boot, zIPL, aboot, and other backends.

## Risks
Backends must implement mandatory `query`, `get_name`, and `write_config` vfuncs. The default atomic=true can be wrong for a backend that forgets to override non-atomic behavior.

## Test Signals
Interface dispatch tests should verify each backend's name/query/write path and default handling for optional hooks.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bootloader.c -->
