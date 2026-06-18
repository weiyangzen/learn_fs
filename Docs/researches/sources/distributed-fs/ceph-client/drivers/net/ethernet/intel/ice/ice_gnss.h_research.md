# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_gnss.h

## Purpose
Defines constants, state, and conditional declarations for `ice` GNSS support.

## Important APIs, types, and functions
- `struct gnss_serial` stores the PF backpointer, kthread worker, and delayed read work.
- Constants define the E810T GNSS I2C bus, u-blox address/registers, polling intervals, maximum write size, and AdminQ I2C chunk limits.
- `ice_gnss_init()`, `ice_gnss_exit()`, and `ice_gnss_is_module_present()` are declared when `CONFIG_GNSS` is enabled and stubbed otherwise.

## Control flow
The header has no runtime flow, but its `IS_ENABLED(CONFIG_GNSS)` guard compiles GNSS support into either real calls or no-op/false stubs.

## State and persistence behavior
The only defined state is the in-memory `gnss_serial` object, which is owned through `pf->gnss_serial` by the implementation.

## Dependencies and integration points
Requires `struct ice_pf`, `struct ice_hw`, kthread worker types, and AdminQ I2C field macros from surrounding driver headers. It is consumed by probe and teardown code to avoid scattering `CONFIG_GNSS` conditionals.

## Risks
Constants encode u-blox ZED-F9T behavior and AdminQ limits. Changing them without matching hardware documentation can break data transfer or polling rate. Stubs must remain behaviorally safe for callers that do not check `CONFIG_GNSS`.

## Test signals
Build both `CONFIG_GNSS=y/m` and disabled configurations. Runtime coverage should confirm the public functions are no-ops when disabled and fully register/deregister GNSS when enabled.
