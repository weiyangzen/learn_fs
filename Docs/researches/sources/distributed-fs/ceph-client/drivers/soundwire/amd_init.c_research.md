# sources/distributed-fs/ceph-client/drivers/soundwire/amd_init.c

## Purpose
Provides the AMD SoundWire initialization library used by an ACP/DSP parent driver to create and start per-link `amd_sdw_manager` platform devices. It enables ACP SoundWire pads, registers manager child devices from ACPI and hardware resources, starts each manager, and reports discovered SoundWire peripherals back to the caller.

## Important APIs, Types, and Functions
Exported namespace functions are `sdw_amd_probe()`, `sdw_amd_exit()`, and `sdw_amd_get_slave_info()` in namespace `SOUNDWIRE_AMD_INIT`. Internal helpers are `amd_enable_sdw_pads()`, `sdw_amd_probe_controller()`, `sdw_amd_startup()`, and `sdw_amd_cleanup()`. The file consumes `struct sdw_amd_res`, `struct sdw_amd_ctx`, `struct acp_sdw_pdata`, and `struct amd_sdw_manager` from `sdw_amd.h`, plus `amd_sdw_manager_start()` from `amd_init.h`.

## Control Flow
`sdw_amd_probe()` calls `sdw_amd_probe_controller()` to validate resources, fetch the ACPI device, enable pads according to `link_mask`, allocate a context, and register one `amd_sdw_manager` platform device per enabled link. Each child receives the shared ACP MMIO resource, ACPI fwnode, instance number, ACP revision, and ACP shared-register lock. If any registration fails, already-created platform devices are unregistered and the context is freed. After child creation, `sdw_amd_startup()` fetches each child's `amd_sdw_manager` drvdata and calls `amd_sdw_manager_start()`. `sdw_amd_exit()` unregisters child devices and frees the optional peripheral list plus context. `sdw_amd_get_slave_info()` walks every enabled manager bus and returns a flex-array list of `struct sdw_slave *`.

## State and Persistence Behavior
The persistent runtime object is `struct sdw_amd_ctx`, which records link count, link mask, registered child platform devices, and a lazily allocated peripheral list. Pad state is programmed in ACP registers by clearing pulldown bits and enabling keeper bits. Platform devices own their own manager state after registration. `sdw_amd_get_slave_info()` allocates `ctx->peripherals` each time it succeeds; callers must account for previous allocation if called repeatedly.

## Dependencies and Integration Points
The library depends on ACPI, platform-device registration, MMIO register access, and AMD ACP resources supplied by a parent driver. It integrates with `amd_manager.c` through the platform driver name `amd_sdw_manager`, the platform data structure, and `amd_sdw_manager_start()`. It exports symbols for external ACP/DSP drivers rather than registering an independent bus.

## Risks
The `sdw_res` resource is allocated with cleanup scope and passed to `platform_device_register_full()`, relying on the platform core to copy resources before the scoped pointer is freed. `sdw_pdata` and `pdevinfo` are stack arrays, also relying on registration copying platform data. Pad enablement supports only link masks 1, 2, or 3. `sdw_amd_get_slave_info()` does not free an existing `ctx->peripherals` before allocating a new one. Startup failures after some managers have started are returned without cleanup in `sdw_amd_probe()`, so parent error handling must call `sdw_amd_exit()`.

## Test Signals
Key tests include ACPI resource discovery, link masks for SDW0, SDW1, and both links, unsupported link masks, platform-device registration failure injection, manager startup failure, probe/exit leak checks, ACP pad register programming, and `sdw_amd_get_slave_info()` with zero, one, and multiple slaves across both links.
