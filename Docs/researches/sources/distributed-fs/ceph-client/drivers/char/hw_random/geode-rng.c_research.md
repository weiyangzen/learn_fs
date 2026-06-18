# sources/distributed-fs/ceph-client/drivers/char/hw_random/geode-rng.c

## Purpose
This legacy driver exposes the AMD Geode LX RNG to hwrng. It manually scans for the Geode AES PCI device, maps MMIO, polls the RNG status register, and reads 32-bit data words.

## Important APIs, Types, and Functions
- `struct amd_geode_priv` stores PCI reference and mapped MMIO base.
- `geode_rng_data_present()` polls `GEODE_RNG_STATUS_REG` with small delays.
- `geode_rng_data_read()` reads `GEODE_RNG_DATA_REG`.
- `geode_rng_init()` scans PCI IDs, maps BAR0, sets hwrng private data, and registers.
- `geode_rng_exit()` unregisters and frees resources.

## Control Flow
Module init finds a matching PCI device, allocates private data, maps the register window, and registers the global hwrng object. Core reads use the older `data_present`/`data_read` API. Module exit unregisters, unmaps, drops the PCI device reference, and frees private state.

## State and Persistence Behavior
Global `geode_rng` holds one private pointer. No hardware enable/disable hooks are implemented. All persistent state is the mapping and PCI reference.

## Dependencies and Integration Points
It depends on x86 PCI, Geode LX AES PCI ID, hwrng core, and MMIO mapping.

## Risks
Manual PCI scanning supports a single device and no hotplug binding. There is no explicit hardware health check beyond a nonzero status register. The older `data_read` path returns four bytes whenever called.

## Test Signals
Test no-device, zero BAR, ioremap failure, hwrng registration failure cleanup, status polling, and module unload resource balancing.
