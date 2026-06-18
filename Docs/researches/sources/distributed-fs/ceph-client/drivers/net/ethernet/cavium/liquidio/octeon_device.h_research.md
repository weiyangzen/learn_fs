# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/octeon_device.h

## Purpose
Defines the central LiquidIO Octeon device model, device states, PCI IDs, interrupt bits, BAR/window mappings, dispatch table structures, console caches, chip callback table, board and firmware metadata, SR-IOV bookkeeping, MSI-X vector records, devlink/switchdev state, and public core-device APIs.

## Important APIs, Types, and Functions
Important enums and constants include Octeon PCI IDs, CN23xx revisions and subsystem IDs, PCI swap modes, firmware load states, Octeon device states from `OCT_DEV_BEGIN_STATE` through `OCT_DEV_IN_RESET`, interrupt masks, BAR1 mapping flags, and private ethtool flags. Important structs are `octeon_dispatch`, `octeon_dispatch_list`, `octeon_mmio`, `octeon_reg_list`, `octeon_console`, `octeon_board_info`, `octeon_fn_list`, `cvmx_bootmem_named_block_desc`, `oct_fw_info`, `cavium_wk`, `cavium_wq`, `octdev_props`, `octeon_pf_vf_hs_word`, `octeon_sriov_info`, `octeon_ioq_vector`, `lio_vf_rep_list`, `lio_devlink_priv`, and the large `octeon_device`.

## Control Flow
The header has no runtime flow, but its status constants define the staged initialization and teardown switch used by main drivers. Function pointers in `octeon_fn_list` allow chip-specific code to provide register setup, mailbox, reset, BAR1, queue, and interrupt operations while common code drives the sequence.

## State and Persistence Behavior
`struct octeon_device` is the long-lived root object for one PCI function. It persists queue pointers, queue masks, response lists, dispatch entries, console addresses, firmware info, board info, SR-IOV settings, VF MAC/VLAN/link/spoof state, mailbox pointers, link stats, devlink mode, and coalescing settings for the device lifetime.

## Dependencies and Integration Points
Includes Linux interrupt and devlink headers. It is consumed across the LiquidIO driver: PF/VF main, device core, IQ/DROQ, console, ethtool, network, mailbox, SR-IOV, and representor code. It links chip-specific implementations to common code through `octeon_fn_list`.

## Risks
This header is high-blast-radius. Any size or semantic change to `octeon_device`, status constants, queue maxima, or callback contracts affects initialization, interrupt handling, netdev setup, and teardown. Several arrays are sized by maximum possible queues or VFs, so mismatches with `octeon_config.h` can cause out-of-bounds use or inaccessible queues. Locking expectations are encoded but not enforced by types.

## Test Signals
Full build coverage for PF and VF, staged init/teardown, SR-IOV enable/disable, devlink switchdev representors, mailbox setup/free, console initialization, interrupt vector setup, queue allocation, ethtool private flags, and static analysis for array bounds and callback null checks are important signals.
