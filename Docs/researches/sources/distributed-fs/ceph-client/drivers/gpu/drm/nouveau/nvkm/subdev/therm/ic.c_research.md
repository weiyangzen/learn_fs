# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/ic.c

## Purpose
Discovers external thermal monitoring ICs on the primary I2C bus using VBIOS extdev hints or a static probe list.

## Important APIs, Types, And Functions
`nvkm_therm_ic_ctor()` drives discovery. `probe_monitoring_device()` requests an I2C module, instantiates a client, runs driver detection, and stores `therm->ic` on success.

## Control Flow
Constructor finds the primary I2C bus, first tries LM89 and ADT7473 addresses from VBIOS extdev entries, honors VBIOS skip-probe flags, then probes a static list of common monitor chips and addresses.

## State, Persistence, And Dependencies
State is the registered I2C client pointer in `therm->ic`; device-managed allocations and I2C core own client lifetime after registration.

## Integration Points
Depends on Nouveau I2C bus probing, VBIOS extdev parsing, Linux I2C module autoloading, and lm_sensors-compatible chip drivers.

## Risks
Probing can instantiate then unregister clients on failed detection. Static probing risks touching unexpected devices unless VBIOS requests skip-probe.

## Test Signals
Signals include debug logs naming detected ICs, loaded I2C drivers, and stable thermal reads when external monitor support is active.
