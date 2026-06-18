# sources/distributed-fs/ceph-client/drivers/soundwire/intel_init.c

## Purpose

`intel_init.c` is the Intel SoundWire controller initialization library used by the parent Intel audio driver. It scans controller resources, creates one auxiliary link device per enabled SoundWire link, collects link Cadence buses and slaves, starts links after parent DSP power-up, dispatches shared IRQ and wake events, and cleans up all auxiliary devices.

## Important APIs, types, and functions

- `sdw_intel_probe()` allocates a `struct sdw_intel_ctx` and registers auxiliary link devices.
- `sdw_intel_startup()` starts all enabled links by calling `intel_link_startup()`.
- `sdw_intel_exit()` resumes children, unregisters auxiliary devices, and frees context arrays.
- `sdw_intel_thread()` is the exported threaded IRQ dispatcher that calls `sdw_cdns_irq()` for each link in `ctx->link_list`.
- `sdw_intel_process_wakeen_event()` forwards a shared wake event to every enabled link.
- `intel_link_dev_register()` builds each `sdw_intel_link_dev`, maps classic versus extended register layouts, fills `link_res`, and registers the auxiliary device.
- `sdw_intel_probe_controller()` owns controller-level discovery, context allocation, link mask handling, link list creation, and flattened peripheral array construction.

## Control flow

The parent driver calls `sdw_intel_probe()` after ACPI scan and passes `sdw_intel_res`. The controller probe verifies ACPI handle/count, allocates `ctx` and link-device pointer array, initializes shared SHIM lock and link mask, then registers auxiliary devices for enabled links. Each auxiliary device probes separately in `intel_auxdevice.c`; after add, this file retrieves the Cadence pointer from auxiliary driver data, adds the link to `ctx->link_list`, and counts slaves on the bus. It then builds a flex-array of all slave pointers for parent use.

Startup is a second phase. `sdw_intel_startup()` iterates enabled links, calls `intel_link_startup()`, and holds a parent runtime PM reference for links without clock-stop quirks. Exit first resumes child devices for each bus to avoid tearing down suspended devices, then disables PM, unregisters auxiliary devices, drops parent references where applicable, frees peripherals, link array, and context.

## State and persistence behavior

`struct sdw_intel_ctx` stores link count, link mask, MMIO base metadata, ACPI handle, shared SHIM mask/lock, link list, per-link auxiliary pointers, and a flattened peripherals array. The auxiliary device owns each `sdw_intel_link_res`. The controller-level `shim_mask` tracks powered links across all auxiliary drivers. No persistent on-disk state exists; hardware state is managed by the per-link driver.

## Dependencies and integration points

This file depends on ACPI, Linux auxiliary bus, PM runtime, Cadence IRQ handling, and Intel link driver entry points declared in `intel_auxdevice.h`. Its exported namespace is `SOUNDWIRE_INTEL_INIT`, consumed by parent Intel audio/SOF code.

## Risks and edge cases

- Probe cannot use devm allocation because it may run from a workqueue; all error paths must manually free link arrays and auxiliary devices.
- If auxiliary probe fails to set driver data, the error path adjusts the loop index to unregister the just-created device; this is delicate.
- Cleanup assumes enabled links have valid `ctx->ldev[i]` pointers.
- `sdw_intel_startup_controller()` does not aggregate or check `intel_link_startup()` return values, so startup failures may be hidden.
- Peripheral array size is computed from slaves visible immediately after auxiliary probe; delayed enumeration later can make the snapshot stale.
- IRQ dispatch walks all registered links and calls Cadence IRQ even if one link has problems.

## Test signals

Test ACPI missing handle, zero link count, sparse link masks, auxiliary add/probe failure, startup with a disabled link, cleanup after partial probe, IRQ handling with multiple links, wake forwarding, and exit while children are runtime suspended. Static review should focus on manual lifetime/error paths and the ignored startup return value.
