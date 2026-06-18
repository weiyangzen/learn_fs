# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_dcb.h

## Purpose
`ixgbe_dcb.h` defines the shared Data Center Bridging configuration model and public DCB helper APIs for ixgbe. It describes DCB support capabilities, traffic-class bandwidth allocation, PFC mode, the aggregate `ixgbe_dcb_config`, error constants, credit limits, and hardware initialization entry points.

## Important APIs, Types, And Functions
- Constants define maximum packet buffers, user priorities, bandwidth groups, TX/RX direction indexes, DCB errors, and capability flags.
- `enum strict_prio_type` distinguishes no strict priority, group strict priority, and link strict priority.
- `struct dcb_support`, `struct tc_bw_alloc`, `struct tc_configuration`, `struct dcb_num_tcs`, and `struct ixgbe_dcb_config` are the main configuration and capability structures.
- `enum dcb_pfc_type` tracks disabled, full, TX-only, and RX-only PFC settings at the traffic-class level.
- Public APIs declare unpack helpers, TC credit calculation, CEE and IEEE hardware configuration, PFC configuration, ETS configuration, and UP-to-TC hardware readback.
- Credit constants define 64-byte quantum, refill/max limits, TSO sizing, and minimum TSO credit requirements.

## Control Flow
Adapter-level DCB setup populates `ixgbe_dcb_config`, then generic DCB code uses the declarations here to calculate credits and unpack arrays for hardware programming. Netlink handlers update either temporary or active instances of these structures before `ixgbe_dcb.c` and chip-specific files apply them to registers.

## State And Persistence
The header defines in-memory state owned by `struct ixgbe_adapter`, especially `adapter->dcb_cfg` and `adapter->temp_dcb_cfg`. This state is runtime configuration and is reapplied to hardware during DCB changes, traffic-class setup, and resets. It is not persisted to disk by the driver.

## Dependencies And Integration Points
The header depends on Linux `dcbnl.h` and ixgbe hardware types. It is included by generic DCB code, chip-specific DCB register programming files, and DCB netlink handlers. Its structures form the contract between user-requested DCBNL settings and MMIO programming.

## Risks
- Array dimensions are fixed at eight TCs/priorities; callers must validate indexes from netlink or hardware before writing arrays.
- Error constants are negative driver-local values, not errno-style for every case; call sites must translate or preserve them intentionally.
- Credit constants encode hardware limits. Changing them can silently create invalid register fields or insufficient credits for jumbo/TSO traffic.
- `dcb_cfg_version` is marked unused, so external consumers should not assume versioned persistence semantics.

## Test Signals
Compile-time coverage of all DCB users, DCBNL set/get round trips, credit calculation tests at boundary bandwidth values, PFC mode transitions, traffic-class count changes, and hardware register readback after CEE/IEEE configuration are the key signals.
