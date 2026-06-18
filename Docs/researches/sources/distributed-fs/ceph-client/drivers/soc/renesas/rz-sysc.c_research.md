# sources/distributed-fs/ceph-client/drivers/soc/renesas/rz-sysc.c

## Purpose

`rz-sysc.c` is the generic Renesas RZ system-controller driver. It registers SoC identity from per-SoC data files and exposes the controller MMIO region as a syscon regmap with SoC-specific read/write allowlists.

## Important APIs, Types, and Functions

`struct rz_sysc` stores base and device. `rz_sysc_soc_init()` parses the compatible into a `soc_id`, reads device ID/revision fields through `rz_sysc_soc_id_init_data`, validates expected ID, prints identity, and calls `soc_device_register()`. `rz_sysc_probe()` maps MMIO, calls identity setup, creates a `regmap_config`, initializes MMIO regmap, and registers it with `of_syscon_register_regmap()`.

## Control Flow

Subsys init registers the platform driver. Probe selects match data compiled for enabled SoCs, maps resource 0, performs SoC registration, configures 32-bit/stride-4 fast regmap using callbacks from the data provider, and publishes it as syscon.

## State and Persistence Behavior

Per-device state is devm-managed, but registered `soc_device` is not paired with an unregister action in this file. Hardware SYS registers persist outside driver memory. The regmap lives for the platform device lifetime.

## Dependencies and Integration Points

It depends on `rz-sysc.h`, per-SoC descriptors, platform MMIO, regmap-mmio, syscon registration, and soc bus. Peripheral drivers access the exposed syscon by phandle.

## Risks and Edge Cases

Compatible parsing assumes a comma and hyphen exist; malformed compatible strings could produce invalid pointer arithmetic. The size cap for `soc_id` uses `strscpy()` with computed length, so off-by-one semantics need review when adding long compatibles. No `soc_device_unregister()` action means unbind is not symmetrical, though bind attrs are suppressed.

## Test Signals

Probe each supported compatible, validate soc-bus entries, ID mismatch rejection, syscon lookup by clients, regmap allowlist enforcement, and malformed/long compatible resilience under test DT overlays.
