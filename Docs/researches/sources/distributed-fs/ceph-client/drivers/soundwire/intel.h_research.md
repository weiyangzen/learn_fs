# sources/distributed-fs/ceph-client/drivers/soundwire/intel.h

## Purpose

`intel.h` is the local Intel SoundWire link header shared by the Intel init, auxiliary-device, classic SHIM, ACE2.x, debugfs, and common bus files. It defines the per-link resource contract, runtime Intel wrapper, BPT context, vendor-specific property storage, PDI type enum, MMIO helper functions, and inline dispatch wrappers for platform-specific hardware ops.

## Important APIs, types, and functions

- `struct sdw_intel_link_res` carries parent-provided resources: hardware ops, MMIO bases, SHIM/ALH/SHIM-VS pointers, IRQ, parent callbacks, locks, masks, clock-stop quirks, link mask, Cadence pointer, link-list node, and HDA bus pointer.
- `struct sdw_intel_bpt` stores HDA BPT TX/RX stream handles, DMA buffers, and computed transfer sizes.
- `struct sdw_intel` embeds `struct sdw_cdns`, link id, resource pointer, startup flag, BPT context, and optional debugfs root.
- `struct sdw_intel_prop` holds Intel-specific firmware properties used by ACE2.x vendor-specific ACTMCTL programming.
- Inline register helpers wrap `readl/writel/readw/writew`.
- `SDW_INTEL_CHECK_OPS()` and `SDW_INTEL_OPS()` implement guarded hardware-op dispatch.
- Inline wrappers such as `sdw_intel_link_power_up()`, `sdw_intel_start_bus()`, `sdw_intel_register_dai()`, `sdw_intel_sync_go()`, and `sdw_intel_get_link_count()` hide generation differences from call sites.
- Common bus prototypes expose `intel_start_bus()`, resume variants, `intel_stop_bus()`, and common bank-switch callbacks.

## Control flow

The header itself has no runtime control path, but it defines the indirection model. `intel_init.c` fills `sdw_intel_link_res` for each auxiliary link. `intel_auxdevice.c` converts that resource into `struct sdw_intel` plus Cadence bus state, then all runtime operations call the inline wrappers. The wrappers check whether a generation-specific operation exists and either invoke it or return a default such as `-ENOTSUPP`, `false`, or four links for older hardware.

## State and persistence behavior

The header defines the state layout but does not mutate state. Important lifetimes are split: `sdw_intel_link_res` belongs to the auxiliary link device, `sdw_intel` is device-managed under the auxiliary driver, BPT DMA resources are opened/closed per BPT transaction, and the shared SHIM mask/lock are owned by the controller context. Hardware state is accessed through MMIO pointers and HDA multi-link helpers selected by the ops table.

## Dependencies and integration points

The header depends on SoundWire public types, Cadence local types, HDA bus forward declaration, and Intel public resource/callback definitions from `linux/soundwire/sdw_intel.h`. It is the main integration seam between older CNL-style ops in `intel.c`, LunarLake/ACE2.x ops in `intel_ace2x.c`, common bus handling in `intel_bus_common.c`, auxiliary-device binding in `intel_auxdevice.c`, and controller enumeration in `intel_init.c`.

## Risks and edge cases

- Inline wrappers return `-ENOTSUPP` for missing ops; callers must distinguish unsupported hardware from transient failures.
- The default link count is four, which is correct for older generations but unsafe if used accidentally on newer hardware without a real `get_link_count`.
- `sdw_intel_link_res` combines shared and per-link pointers. Incorrect initialization of `shim_lock`, `shim_mask`, `link_mask`, or `hbus` can corrupt shared power management.
- ACE2.x and older hardware share the same `struct sdw_intel`; any future field additions must preserve both code paths.

## Test signals

Build both classic Intel and ACE2.x configurations, with and without `CONFIG_DEBUG_FS`. Static checks should ensure every wrapper has a corresponding ops field and every ops user handles unsupported returns. Probe tests should confirm resources are populated correctly for non-extended and extended (`res->ext`) controller layouts.
