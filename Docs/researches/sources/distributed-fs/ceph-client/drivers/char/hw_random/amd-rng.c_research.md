# sources/distributed-fs/ceph-client/drivers/char/hw_random/amd-rng.c

## Purpose
This legacy driver exposes the AMD 768/76x chipset RNG through the hwrng core. It manually scans PCI IDs, maps PM I/O space, enables RNG and PM I/O bits in PCI config space, and reads 32-bit RNG data when `RNGDONE` is set.

## Important APIs, Types, and Functions
- `struct amd768_priv` holds mapped I/O base, PCI device reference, and PM base.
- `amd_rng_init()` enables RNG and PMIO PCI config bits.
- `amd_rng_cleanup()` disables the RNG bit.
- `amd_rng_read()` polls `RNGDONE`, sleeps per datasheet when waiting, and reads `RNGDATA`.
- `amd_rng_mod_init()` scans PCI, requests I/O region, maps it, and registers `amd_rng`.

## Control Flow
Module init finds a matching PCI bridge, extracts the PM base, claims the RNG PM I/O region, maps it, stores private data, and registers the hwrng. When selected, core init flips enable bits. Reads loop while space remains, waiting at most one delay budget per requested word batch. Module exit unregisters, unmaps, releases the I/O region, drops the PCI reference, and frees private state.

## State and Persistence Behavior
Global `amd_rng` holds a pointer to one allocated private structure. Hardware enable bits persist until cleanup or module unload. There is no per-device PCI driver binding, so the code intentionally avoids claiming the bridge as a PCI driver.

## Dependencies and Integration Points
It depends on x86/PCI, `HAS_IOPORT_MAP`, hwrng core, PCI config space access, and I/O port resource management. PCI IDs are exported with `MODULE_DEVICE_TABLE`.

## Risks
Manual PCI scanning supports only one device and must balance `pci_dev_put()` correctly. `amd_rng_read()` returns partial data on timeout and zero for nonblocking unavailable data. Config-space writes can affect chipset power-management behavior outside the RNG.

## Test Signals
Test no-device, zero PMBASE, busy I/O region, `ioport_map()` failure, hwrng registration failure cleanup, enable/disable config bits, blocking and nonblocking reads, and module unload resource release.
