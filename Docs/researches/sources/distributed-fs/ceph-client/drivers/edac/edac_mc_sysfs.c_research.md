# sources/distributed-fs/ceph-client/drivers/edac/edac_mc_sysfs.c

## Purpose
This file implements sysfs support for EDAC memory controllers and DIMM/rank devices. It exposes global module parameters, per-DIMM metadata/counters, per-controller counters, reset controls, optional scrub-rate controls, and the parent `mc` device under the EDAC bus.

## Important APIs, Types, And Functions
Global tunables are `edac_mc_log_ue`, `edac_mc_log_ce`, `edac_mc_panic_on_ue`, and `edac_mc_poll_msec`, with getters `edac_mc_get_log_ue()`, `edac_mc_get_log_ce()`, `edac_mc_get_panic_on_ue()`, and `edac_mc_get_poll_msec()`. `edac_set_poll_msec()` validates new polling intervals and calls `edac_mc_reset_delay_period()`.

DIMM helpers include `edac_create_dimm_object()`, label/location/size/type/mode/count show functions, and label store. MC helpers include `edac_create_sysfs_mci_device()`, `edac_remove_sysfs_mci_device()`, `edac_mc_sysfs_init()`, and `edac_mc_sysfs_exit()`.

## Control Flow
EDAC module initialization calls `edac_mc_sysfs_init()`, which creates the parent `mc` device on the EDAC bus. When a controller is registered, `edac_create_sysfs_mci_device()` configures `mci->dev` as `mcN`, attaches optional driver groups, adds the device, creates populated DIMM/rank child devices, and creates debugfs nodes. Removal unregisters debugfs, unregisters DIMM devices, and deletes the MC device. Module exit unregisters the parent `mc` device.

Sysfs reads format live EDAC state such as DIMM labels, locations, memory type, device width, EDAC mode, CE/UE counts, controller size, no-info counters, max location, and seconds since reset. `reset_counters` clears controller, csrow/channel, and DIMM counters. `sdram_scrub_rate` appears only when driver callbacks exist and delegates set/get operations to the low-level MC driver.

## State And Persistence
Global module parameters persist for the EDAC module lifetime and affect logging, panic behavior, and polling interval. Per-DIMM labels are mutable through sysfs and persist while the DIMM object exists. Counter reset changes live in-memory EDAC counters only. The `mci_pdev` parent device persists from EDAC sysfs init to exit.

## Dependencies And Integration Points
The file depends on EDAC MC core structures, the EDAC bus, Linux device/sysfs APIs, runtime PM calls, and debugfs creation. Low-level drivers indirectly use this file when they call `edac_mc_add_mc()` and expose optional scrub callbacks.

## Risks
`edac_set_poll_msec()` rejects intervals under 1000 ms, while generic EDAC device sysfs has looser behavior, so MC and device polling policies differ. `dimmdev_label_store()` rejects empty or oversized labels but allows arbitrary non-newline bytes copied from sysfs input. Only populated DIMMs are exposed as child devices, so missing expected DIMM nodes may mean zero `nr_pages` rather than allocation failure.

## Test Signals
Signals include module parameter read/write behavior, poll-period reset for active controllers, MC device creation under the EDAC bus, child DIMM/rank creation only for populated DIMMs, label store validation, reset counter coverage, conditional scrub-rate permissions, debugfs node creation/removal, and clean parent `mc` unregister at exit.
