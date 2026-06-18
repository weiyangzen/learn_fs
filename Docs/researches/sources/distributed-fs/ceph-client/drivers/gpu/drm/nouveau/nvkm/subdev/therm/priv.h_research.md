# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/priv.h

## Purpose
Defines private Nouveau thermal structures, callback tables, and cross-file helper declarations.

## Important APIs, Types, And Functions
`struct nvkm_fan` stores fan backend state. `struct nvkm_therm_func` defines chip callbacks for init/fini/intr, PWM, temperature, fan sense, alarm programming, and clockgating. The header declares fan, sensor, PWM, chip, and clockgating helpers.

## Control Flow
Common and chip-specific C files include this header to populate function tables, allocate backends, and call shared helpers.

## State, Persistence, And Dependencies
The header stores no runtime state itself but defines the layout of allocated fan objects and callback contracts.

## Integration Points
Integrates all thermal chip implementations with the public `subdev/therm.h` interface, VBIOS types, and fan/sensor helper files.

## Risks
Changing callback semantics affects many chip families. `container_of` macros require embedded object layout to remain correct.

## Test Signals
Compile coverage across all thermal objects and successful runtime construction for multiple chip generations are the main signals.
