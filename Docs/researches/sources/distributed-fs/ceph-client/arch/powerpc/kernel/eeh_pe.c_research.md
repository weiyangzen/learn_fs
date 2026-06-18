<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/eeh_pe.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/eeh_pe.c

## Purpose
`eeh_pe.c` manages EEH Processing Element topology and PE-local operations. It creates PHB roots, inserts/removes device/bus/VF PEs, traverses PE trees, tracks isolation/recovery state, restores PCI BAR/config data after reset, and resolves PE location/bus information.

## Important APIs, Types, And Functions
Important globals are `eeh_pe_aux_size` and `eeh_phb_pe`. Public functions include `eeh_set_pe_aux_size()`, `eeh_phb_pe_create()`, `eeh_wait_state()`, `eeh_phb_pe_get()`, `eeh_pe_next()`, `eeh_pe_traverse()`, `eeh_pe_dev_traverse()`, `eeh_pe_get()`, `eeh_pe_tree_insert()`, `eeh_pe_tree_remove()`, `eeh_pe_update_time_stamp()`, exported `eeh_pe_state_mark()`, exported `eeh_pe_mark_isolated()`, `eeh_pe_dev_mode_mark()`, `eeh_pe_state_clear()`, `eeh_pe_restore_bars()`, `eeh_pe_loc_get()`, `eeh_pe_loc_get_bus()`, `eeh_pe_bus_get()`, and `eeh_pe_bus_get_nolock()`.

## Control Flow
PHB PEs are allocated at host bridge discovery and form roots. Device insertion searches by PE address, reuses existing PEs, clears invalid ancestors during recovery hotplug, or allocates device/VF PEs under the requested parent or PHB. Removal detaches the `eeh_dev`, frees empty non-recovering PEs, or marks empty recovering PEs invalid for later cleanup. State marking/clearing walks the affected subtree and updates PCI channel state and config-blocking. BAR restore handles bridges and endpoint devices differently, using EEH config ops and link checks. `eeh_wait_state()` loops on firmware unavailable state with bounded waits.

## State And Persistence
PE tree state is runtime-only and includes parent/child lists, attached `eeh_dev` lists, state bits, freeze counters, timestamps, primary bus cache, and optional auxiliary data. Saved config space resides in `eeh_dev`.

## Dependencies And Integration Points
It integrates with platform `eeh_ops`, PCI controller/bridge metadata, PCI resource and config definitions, OF location-code properties, PCI rescan/remove locking, and EEH driver recovery cleanup.

## Risks
Tree mutation during recovery is delicate; invalid marking avoids freeing nodes while traversals are active. Config-space access on restricted PEs can fence a PHB. Bridge link power/link training loops can delay recovery. Bus lookup without locks must be used only when the caller already protects PCI topology.

## Test Signals
Signals include PE tree creation for PHBs and hotplug devices, VF PE insertion/removal, subtree traversal, repeated unavailable firmware state handling, BAR restore after reset, location-code output, and cleanup of invalid empty PEs after recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/eeh_pe.c -->
