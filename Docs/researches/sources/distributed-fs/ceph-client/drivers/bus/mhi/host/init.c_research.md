# sources/distributed-fs/ceph-client/drivers/bus/mhi/host/init.c

## Purpose

`init.c` is the MHI host bus and controller lifecycle implementation. It registers the `mhi` bus, allocates controller-private runtime structures, parses controller channel/event configuration, sets up IRQs and DMA-backed MHI contexts, creates the root controller `mhi_device`, and manages MHI client device probe/remove and driver registration. It also owns sysfs attributes for controller-visible metadata and control actions such as serial number, OEM PK hash, SoC reset, and optional EDL trigger.

## Important APIs, Types, And Functions

- Exported controller APIs: `mhi_register_controller()`, `mhi_unregister_controller()`, `mhi_alloc_controller()`, `mhi_free_controller()`, `mhi_prepare_for_power_up()`, and `mhi_unprepare_after_power_down()`.
- Device/client APIs: `mhi_alloc_device()`, `__mhi_driver_register()`, `mhi_driver_unregister()`, and the `mhi_bus_type` bus object.
- Context setup: `mhi_init_dev_ctxt()`, `mhi_deinit_dev_ctxt()`, `mhi_init_mmio()`, `mhi_init_chan_ctxt()`, and `mhi_deinit_chan_ctxt()`.
- Config parsing: `parse_ch_cfg()`, `parse_ev_cfg()`, and `parse_config()` translate `struct mhi_controller_config` into allocated `struct mhi_chan` and `struct mhi_event` arrays.
- String tables for execution environment, device transition, channel state type, and PM state are generated from macros shared with `internal.h` and `trace.h`.

## Control Flow

Controller drivers call `mhi_register_controller()` after filling MMIO, IRQ, register access, runtime PM, and callback fields. Registration validates required callbacks and hardware resources, parses the supplied config, allocates command rings, initializes locks/workqueues/tasklets, selects DMA mapping strategy, allocates a controller id, requests IRQs, creates the root `mhi_device`, adds optional EDL sysfs support, and creates debugfs. Power preparation is separate: `mhi_prepare_for_power_up()` allocates the device context, discovers BHI/BHIe offsets, clears RDDM state if needed, and prepares an RDDM download table when configured.

`mhi_init_mmio()` programs context base addresses, MHI control/data address limits, event-ring counts, hardware event-ring counts, channel doorbell addresses, event doorbell addresses, wake doorbell address, and command doorbell address. Per-channel context creation is delayed until a client opens a channel through transfer preparation.

The bus probe path calls `mhi_device_get_sync()` to wake the device, validates that required callbacks exist for UL/DL/offload/client-managed rings, installs transfer callbacks on the channel structures, and then calls the client driver's `probe()`. Remove resets both directions, wakes waiters, marks channels suspended/disabled, invokes the client `remove()`, deinitializes channel contexts that had been enabled, and balances outstanding `mhi_device_get_sync()` references.

## State And Persistence Behavior

Most persistent state lives in `struct mhi_controller`: allocated channel/event/cmd arrays, `mhi_ctxt`, DMA ring memory, workqueue, PM locks, wake counters, tasklets, IRQs, root `mhi_dev`, and optional firmware/RDDM image tables. Channel state is mirrored in host-side `mhi_chan->ch_state` and device-visible channel context bits. Ring memory is coherent DMA with alignment enforced by `mhi_alloc_aligned_ring()`. Device objects hold references back to channel structures; `mhi_release_device()` clears `mhi_chan->mhi_dev` so suspend/resume or EE changes can recreate devices.

## Dependencies And Integration Points

This file depends on public MHI definitions in `<linux/mhi.h>`, common protocol definitions in `../common.h` through `internal.h`, Linux driver core bus/device APIs, DMA coherent allocation, IRQ APIs, debugfs hooks, sysfs, and the PM functions implemented in `pm.c`. It is used by transport drivers such as `pci_generic.c`, which provide register accessors, IRQ lists, runtime PM callbacks, and controller configs.

## Risks

The cleanup paths are tightly ordered; failures during config parsing, IRQ setup, or root device creation must free only the pieces already initialized. Doorbell offset bounds checks in `mhi_init_mmio()` are critical because invalid MMIO offsets would corrupt unrelated registers. The code mutates controller config-derived event data when shared MSI is used by PCI glue, so configs declared `static const` versus mutable matter. Client probe error paths call `mhi_unprepare_from_transfer()` even if transfer preparation was not performed by the framework here, so channel state assumptions must stay aligned with client driver behavior. Sysfs EDL trigger directly invokes controller reset paths and must only exist when the controller provides `edl_trigger`.

## Test Signals

Useful signals include successful `mhi` bus registration at postcore init, successful controller registration and power preparation for PCI devices, sysfs attributes under the root MHI device, correct creation/removal of channel devices across EE transitions, IRQ request/free balance under `CONFIG_DEBUG_SHIRQ`, DMA allocation failure injection, invalid channel/event config rejection, and suspend/resume paths that destroy and recreate channel devices without stale `mhi_chan->mhi_dev` pointers.
