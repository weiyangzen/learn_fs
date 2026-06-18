# sources/distributed-fs/ceph-client/drivers/soundwire/master.c

## Purpose

`master.c` creates the Linux device representation for a SoundWire master bus and exposes master DisCo properties through sysfs. It also enables runtime PM on the master device so the master can autosuspend when no children keep the bus active.

## Important APIs, types, and functions

- `sdw_master_device_add()` allocates and registers `struct sdw_master_device`.
- `sdw_master_device_del()` disables runtime PM and unregisters the master device.
- `sdw_master_type` describes the device type, release callback, and runtime PM operations.
- Sysfs attributes expose `revision`, `clk_stop_modes`, `max_clk_freq`, `default_row`, `default_col`, `default_frame_rate`, `dynamic_frame`, `err_threshold`, `clock_frequencies`, and `clock_gears`.
- `master_dev_pm` uses generic runtime suspend/resume callbacks.

## Control flow

The controller driver calls `sdw_master_device_add()` after initializing an `sdw_bus`. The function allocates the master device, sets bus/type/parent/groups/fwnode/DMA mask, names it `sdw-master-controller-link`, registers it, stores shortcuts in `bus->dev` and `bus->md`, and enables autosuspend with a 3 second delay. Deletion disables runtime PM and unregisters the device; the release callback frees the allocation.

## State and persistence behavior

The master device owns sysfs-visible property state indirectly through `md->bus->prop`. Runtime PM state is stored in the device core. No hardware registers are touched here; persistence is limited to the registered device lifetime and property values filled by controller property-reading callbacks.

## Dependencies and integration points

It depends on the SoundWire bus type, `struct sdw_master_device`, Linux device/sysfs APIs, ACPI/fwnode plumbing, and PM runtime. Controllers such as Intel and Qualcomm call this through `sdw_bus_master_add()` and delete through `sdw_bus_master_delete()`.

## Risks and edge cases

- Property sysfs uses `sprintf` and assumes arrays and counts in `bus->prop` are initialized correctly.
- On `device_register()` failure, ownership transfers to `put_device()` and the caller must not free `md`.
- Runtime PM autosuspend behavior depends on child devices becoming active when attached; buses with no attached slaves autosuspend after the delay.
- `sdw_master_device_del()` assumes `bus->md` and `bus->dev` are valid.

## Test signals

Validate master device names for multiple controller/link ids, sysfs attributes after DisCo property parsing, add failure cleanup, runtime PM autosuspend with no slaves, active child preventing master suspend, and clean deletion during controller unbind.
