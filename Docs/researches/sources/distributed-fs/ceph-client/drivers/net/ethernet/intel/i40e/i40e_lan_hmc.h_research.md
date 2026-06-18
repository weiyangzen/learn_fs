# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_lan_hmc.h

## Purpose
`i40e_lan_hmc.h` declares LAN-specific HMC context structures, object sizes, resource types, HMC model choices, create/delete request structures, and public LAN HMC lifecycle and queue-context APIs.

## Important APIs, types, and functions
- `struct i40e_hmc_obj_rxq` is the software representation of an Rx queue context, including descriptor base, queue length, buffer sizing, split/header options, RSS/flow-control knobs, TPH controls, threshold, and prefetch enable.
- `struct i40e_hmc_obj_txq` is the Tx queue context representation, including descriptor base, queue length, head writeback, TPH controls, ready-list fields, and CRC.
- `enum i40e_hmc_obj_rx_hsplit_0` enumerates Rx header-split modes.
- `struct i40e_hmc_obj_fcoe_cntx` and `struct i40e_hmc_obj_fcoe_filt` reserve FCoE debug-context layouts.
- Object constants define LAN HMC base alignment and context sizes: Tx queue 128 bytes, Rx queue 32 bytes, FCoE context/filter 64 bytes.
- `enum i40e_hmc_lan_rsrc_type` identifies aggregate LAN, Tx, Rx, FCoE context, and FCoE filter resources.
- `enum i40e_hmc_model` selects direct-preferred, direct-only, paged-only, or unknown HMC backing.
- `struct i40e_hmc_lan_create_obj_info` and `struct i40e_hmc_lan_delete_obj_info` carry object operation parameters.
- Public APIs initialize, configure, shut down, clear, and set LAN HMC queue contexts.

## Control flow and behavior
This header is consumed by `i40e_lan_hmc.c`. Callers first initialize object metadata with `i40e_init_lan_hmc()`, configure backing store with `i40e_configure_lan_hmc()`, program queue contexts through the Tx/Rx set/clear APIs, and later release all HMC memory through `i40e_shutdown_lan_hmc()`. The context structs are intentionally wider than some hardware fields so bitfield packing can safely handle fields crossing byte boundaries.

## State and persistence
The declared queue context structs are transient software inputs that become hardware-consumed HMC context bytes when packed. The create/delete info structs are short-lived operation descriptors. Persistent lifecycle state lives in `struct i40e_hmc_info` from `i40e_hmc.h` and in device HMC registers.

## Dependencies and integration points
The header includes generic HMC definitions and forward-declares `struct i40e_hw`. It is part of the queue setup/control path and is coupled to the bit layout tables in `i40e_lan_hmc.c` and to hardware context sizes reported by GLHMC registers.

## Risks and edge cases
- Any change to context struct fields must be reflected in the packing tables or hardware receives incorrect queue context bits.
- The documented "bigger than needed" fields prevent shifts from losing high bits; narrowing them would be risky.
- Queue context size constants must match device expectations and GLHMC-reported object sizes.
- The HMC model enum includes `UNKNOWN`; configuration code rejects it, so callers must select a supported model.

## Test signals
Compile-time users catch API drift. Runtime signals include successful queue context programming, no Tx/Rx hangs after queue enable, direct and paged HMC configuration coverage, and validation that descriptor base/length/buffer-size fields work for normal traffic, jumbo settings, and feature combinations such as header split, TPH, and FCoE where applicable.
