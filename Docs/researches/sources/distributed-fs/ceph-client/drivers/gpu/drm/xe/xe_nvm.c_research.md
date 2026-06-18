
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_nvm.c

## Purpose

`xe_nvm.c` exposes discrete GPU internal NVM regions to the generic Intel DG NVM auxiliary driver when the platform supports GSC NVM access. It builds an auxiliary device with resource windows and platform-specific writable/erase behavior flags.

## Important APIs, Types, and Functions

- Static region table names descriptor, GSC, padding, OptionROM, and DAM regions.
- `xe_nvm_init()` allocates and registers `struct intel_dg_nvm_dev`.
- `xe_nvm_fini()` deletes/uninitializes the auxiliary device on managed teardown.
- `xe_nvm_release_dev()` frees the allocated NVM object.
- Platform policy helpers: `xe_nvm_writable_override()` and `xe_nvm_non_posted_erase()`.

## Control Flow

Initialization exits early when no GSC NVM exists or the device is an SR-IOV VF. It validates `xe->nvm` is empty, allocates the auxiliary device data, reads platform registers to determine write override and non-posted erase behavior, creates BAR resource descriptors for GUNIT and DEBUG NVM windows relative to PCI BAR0, initializes/adds the auxiliary device, stores `xe->nvm`, and registers devm cleanup.

## State and Persistence Behavior

`xe->nvm` points to the auxiliary NVM device while registered. Resource descriptors and region metadata persist in that object. The auxiliary device release callback owns final memory freeing.

## Dependencies and Integration Points

It integrates with `intel_dg_nvm_aux`, PCI resources, GSC/HECI register definitions, PCODE scratch registers, root tile MMIO, SR-IOV mode checks, and DRM logging.

## Risks and Edge Cases

- Unknown platforms in writable override log an error and return `true`, effectively treating access as overridden.
- VFs never expose internal NVM.
- Resource offsets are hard-coded Gen12-era constants and must stay valid for supported platforms.
- Auxiliary device add failure must uninit but not double-free because release semantics differ before/after init.

## Test Signals

Tests should cover no-NVM and VF early exits, each platform policy register path, auxiliary init/add failure injection, resource address calculations, and managed cleanup.
