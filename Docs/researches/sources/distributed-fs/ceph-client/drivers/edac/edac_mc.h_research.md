# sources/distributed-fs/ceph-client/drivers/edac/edac_mc.h

## Purpose
This header declares the EDAC memory-controller core API and common logging/debug helpers used by low-level EDAC drivers. It defines page/MiB conversion macros, EDAC printk macros, debug logging, PCI ID convenience macros, `to_mci()`, and all exported MC lifecycle and error-reporting function prototypes.

## Important APIs, Types, And Functions
Important declarations include `edac_mc_alloc()`, `edac_mc_free()`, `edac_get_owner()`, `edac_mc_add_mc_with_groups()`, `edac_mc_add_mc()`, `edac_has_mcs()`, `edac_mc_find()`, `find_mci_by_dev()`, `edac_mc_del_mc()`, `edac_mc_find_csrow_by_page()`, `edac_raw_mc_handle_error()`, `edac_mc_handle_error()`, and `edac_op_state_to_string()`.

The header also declares `edac_mem_types[]`, `edac_debug_level`, and the shared `edac_layer_name[]` indirectly used by debugfs and error formatting.

## Control Flow
Low-level drivers include this header to allocate a `mem_ctl_info`, register it, optionally provide polling and scrub callbacks, report errors with layer coordinates, and unregister/free on remove. The `edac_mc_add_mc()` macro uses the grouped variant with no extra sysfs attribute groups.

## State And Persistence
The header itself owns no runtime state but exposes access to global EDAC state through extern declarations and macros. It codifies that `struct mem_ctl_info` embeds a `struct device` addressable by `to_mci()`.

## Dependencies And Integration Points
It depends on kernel module, PCI, platform, time, NMI, RCU, completion, kobject, workqueue, and EDAC headers. It is the central integration point between hardware EDAC drivers and the MC core in `edac_mc.c` and `edac_mc_sysfs.c`.

## Risks
Logging macros use raw `printk()` formatting and require valid `mci`/controller pointers. `edac_dbg()` compiles away when debug is disabled, so side effects must not be placed in its arguments. The API allows drivers to supply arbitrary layer indexes to `edac_mc_handle_error()`, relying on runtime validation in the core.

## Test Signals
Compile coverage is the main signal for this header. Runtime validation comes from all low-level MC drivers successfully allocating, adding, reporting errors, exposing sysfs, and deleting controllers through the declared APIs.
