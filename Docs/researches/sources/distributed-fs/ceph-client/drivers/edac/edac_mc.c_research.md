# sources/distributed-fs/ceph-client/drivers/edac/edac_mc.c

## Purpose
This file implements the EDAC memory-controller core. It allocates and frees `mem_ctl_info` topologies, manages the global memory-controller list and owner arbitration, schedules polling, maps errors to DIMMs/csrows, increments counters, emits logs and RAS trace events, and performs optional software scrubbing for correctable errors.

## Important APIs, Types, And Functions
Global state includes exported `edac_op_state`, `mem_ctls_mutex`, `mc_devices`, and `edac_mc_owner`. Allocation/lifecycle APIs are `edac_mc_alloc()`, `edac_mc_free()`, `edac_mc_add_mc_with_groups()`, `edac_mc_del_mc()`, `edac_has_mcs()`, `find_mci_by_dev()`, and `edac_mc_find()`. Error APIs are `edac_mc_handle_error()` and `edac_raw_mc_handle_error()`.

Internal support functions allocate csrow/channel structures (`edac_mc_alloc_csrows()`), allocate DIMMs (`edac_mc_alloc_dimms()`), run polling work (`edac_mc_workq_function()`), reset poll delay (`edac_mc_reset_delay_period()`), find csrow by page (`edac_mc_find_csrow_by_page()`), increment counters, print/log CE/UE events, and scrub memory (`edac_mc_scrub_block()`).

## Control Flow
Low-level MC drivers call `edac_mc_alloc()` with a layer topology. The core computes total DIMMs, virtual csrows, channels, initializes a `struct device`, allocates private data, csrows, channels, and DIMMs, links DIMMs to legacy csrow/channel objects, and returns an `OP_ALLOC` controller. `edac_mc_add_mc_with_groups()` enforces single-owner policy, inserts into the global list, creates sysfs, starts polling work if `mci->edac_check` exists, or marks interrupt mode otherwise. `edac_mc_del_mc()` marks offline, removes from the list, clears owner when last MC is removed, stops work, and removes sysfs.

`edac_mc_handle_error()` normalizes driver-supplied layer coordinates, finds matching DIMMs, builds label and location strings, derives a maximum grain, increments legacy csrow/channel counters, and delegates to `edac_raw_mc_handle_error()`. The raw handler emits a RAS trace event and then logs/increments CE or UE paths. CE handling optionally maps controller pages to CPU physical pages and scrubs the affected block for `SCRUB_SW_SRC`.

## State And Persistence
The global MC list is mutex-protected and RCU-synchronized on deletion. `edac_mc_owner` prevents concurrent ownership by incompatible modules such as GHES and chipset-specific drivers. `mem_ctl_info` owns topology, counters, error descriptor buffer, sysfs device, delayed work, and private data. `edac_raw_error_desc` inside `mci` is reused for each report, which is why interrupt drivers with concurrent paths may need external locking.

## Dependencies And Integration Points
The file depends on EDAC public types, EDAC sysfs helpers, EDAC workqueue helpers, RAS tracepoints, kmap/highmem helpers, optional architecture atomic scrub support, and `edac_module.h`. Every memory-controller driver in this subset integrates through this file's allocation, registration, and reporting APIs.

## Risks
`edac_has_mcs()` returns the inverse of `list_empty()` but uses a local named `ret`, which can confuse readers. The owner check compares string pointers (`edac_mc_owner != mci->mod_name`), so low-level drivers must use stable module-name pointers. `mci->error_desc` is shared mutable state; concurrent interrupt handlers need serialization. Layer coordinates outside configured bounds are corrected to unknown but still reported, preventing crashes at the cost of precision.

## Test Signals
Tests should cover topology allocation for virtual and non-virtual csrows, allocation failure unwind, duplicate MC index/device rejection, owner arbitration, polling start/stop, sysfs creation/removal, layer-coordinate validation, multi-label DIMM matching, no-info counters, CE software scrub invocation, UE panic configuration, and RAS trace emission.
