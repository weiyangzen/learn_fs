# sources/distributed-fs/ceph-client/drivers/char/hw_random/intel-rng.c

## Purpose
This legacy driver exposes Intel 82802/i8xx firmware-hub RNG hardware. It verifies firmware hub presence using temporary FWH read-ID cycles under `stop_machine()`, maps the magic RNG address, enables the RNG, and reads one byte at a time through the hwrng core.

## Important APIs, Types, and Functions
- `intel_rng_data_present()` polls the RNG status data-present bit.
- `intel_rng_data_read()` reads one byte from `INTEL_RNG_DATA`.
- `intel_rng_init()` enables the RNG hardware status bit.
- `intel_rng_cleanup()` disables it.
- `struct intel_rng_hw` captures PCI config registers and temporary FWH mapping for detection.
- `intel_rng_hw_init()` runs under `stop_machine()` to switch FWH to read-ID mode and restore config.
- `intel_rng_mod_init()` scans supported PCI IDs, performs FWH detection unless disabled, maps RNG registers, and registers hwrng.

## Control Flow
Module init finds a known Intel LPC bridge. Unless `no_fwh_detect` skips detection, it reads/possibly modifies BIOS/FWH decode config, maps FWH space, stops the machine, issues read-ID commands, restores state, and verifies manufacturer/device IDs. It then maps the RNG magic address, checks present bit, and registers the hwrng. Core init enables RNG. Reads use the legacy present/read callbacks. Exit unregisters and unmaps.

## State and Persistence Behavior
Global `intel_rng` holds the RNG MMIO pointer. Hardware enable status persists while selected. Detection temporarily modifies PCI config and FWH command state but restores them before returning.

## Dependencies and Integration Points
It depends on x86 PCI bridge IDs, fixed legacy MMIO addresses, `stop_machine()`, hwrng core, and module parameter `no_fwh_detect`.

## Risks
FWH detection manipulates firmware address space and must run with the system stopped; bad restoration can affect firmware flash access. Locked BIOS control can block safe detection. Reads provide only one byte per callback, limiting throughput.

## Test Signals
Test `no_fwh_detect` modes, locked firmware-space behavior, FWH ID success/failure, RNG-present bit failure, enable/disable status bits, registration cleanup paths, and module unload.
