# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_sf_eth.h

## Purpose

`ice_sf_eth.h` defines the Ethernet subfunction auxiliary-device data structures and the public activation/driver-registration API used by ice devlink/dynamic-port code.

## Important APIs, Types, And Functions

- `struct ice_sf_dev` embeds `struct auxiliary_device`, points to the owning `struct ice_dynamic_port`, and stores the allocated `struct ice_sf_priv`.
- `struct ice_sf_priv` links the subfunction device to its `struct devlink_port`.
- `ice_adev_to_sf_dev()` converts an auxiliary device back to `struct ice_sf_dev`.
- `ice_sf_driver_register()` and `ice_sf_driver_unregister()` expose auxiliary driver lifecycle.
- `ice_sf_eth_activate()` and `ice_sf_eth_deactivate()` expose dynamic-port Ethernet SF lifecycle.

## Control Flow

The header itself has no runtime control flow. It establishes the type relationship that lets the auxiliary bus call into `ice_sf_eth.c` and lets devlink dynamic-port code request activation or deactivation.

## State And Persistence

The declared structures own runtime pointers only. The auxiliary device lifetime is tied to activation/deactivation, and the embedded devlink port is created during probe and destroyed during remove. No persistent storage is defined.

## Dependencies And Integration Points

It includes `<linux/auxiliary_bus.h>` and `ice.h`, and is consumed by the SF Ethernet implementation plus any ice code that registers the SF driver or activates dynamic Ethernet subfunctions.

## Risks

- `ice_adev_to_sf_dev()` assumes every matching auxiliary device embeds `struct ice_sf_dev`; misuse with a different auxiliary device type would corrupt pointer interpretation.
- Lifetime is pointer-heavy: `ice_sf_dev`, `ice_dynamic_port`, `ice_sf_priv`, and devlink port lifetimes must stay ordered by the C implementation.

## Test Signals

Compile tests catch declaration drift. Runtime validation should come from SF activation/probe/remove tests that confirm `ice_adev_to_sf_dev()` round trips and that `ice_sf_priv` remains valid until remove completes.
