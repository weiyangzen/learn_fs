# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/phy_ac.c

## Purpose
`phy_ac.c` provides the AC-PHY `struct b43_phy_operations` instance for IEEE 802.11ac Broadcom PHYs. In this snapshot it is a minimal skeleton: it allocates/free AC private state, implements AC-specific PHY mask/set and radio read/write accessors, returns a default channel by band, and stubs TX power recalculation/adjustment.

## Important APIs, Types, and Functions
- `b43_phy_ac_op_allocate()` allocates `struct b43_phy_ac` and stores it in `dev->phy.ac`.
- `b43_phy_ac_op_free()` releases that private state and clears the pointer.
- `b43_phy_ac_op_maskset()` accesses AC PHY registers through `B43_MMIO_PHY_CONTROL` and `B43_MMIO_PHY_DATA`.
- `b43_phy_ac_op_radio_read()` and `b43_phy_ac_op_radio_write()` access radio registers through the newer `B43_MMIO_RADIO24_CONTROL/DATA` path.
- `b43_phy_ac_op_get_default_chan()` chooses channel 11 for 2.4 GHz and channel 36 for 5 GHz.
- `b43_phy_ac_op_recalc_txpower()` returns `B43_TXPWR_RES_DONE`; `b43_phy_ac_op_adjust_txpower()` is empty.
- `b43_phyops_ac` publishes these callbacks to `phy_common.c`.

## Control Flow
`b43_phy_allocate()` selects `b43_phyops_ac` when `dev->phy.type` is `B43_PHYTYPE_AC` and `CONFIG_B43_PHY_AC` is enabled. Common PHY code then calls the vtable during allocation, register access, channel setup, and TX power checks. The implemented AC callbacks are direct MMIO wrappers with no calibration sequence.

## State and Persistence
The only software state owned here is the allocated `struct b43_phy_ac`, currently empty. Hardware state changes occur through the register access callbacks. TX power functions intentionally do not persist calculated state or write hardware values.

## Dependencies and Integration Points
- Includes `b43.h` and `phy_ac.h`.
- Integrated through `struct b43_phy_operations` declared in `phy_common.h`.
- Register constants are supplied by `phy_ac.h`; common lifecycle is driven by `phy_common.c` and `main.c`.

## Risks and Edge Cases
- The operations table lacks several callbacks documented as mandatory in `phy_common.h`, including `prepare_structs`, `init`, `software_rfkill`, `switch_analog`, and `switch_channel`. Common b43 paths call these unconditionally in several places, so AC-PHY enablement can crash or fail without additional implementation.
- TX power control is effectively a no-op, which may be acceptable only for unsupported/skeletal hardware bring-up.
- There is no channel-switch or RF-kill implementation despite AC devices being accepted by versioning and firmware selection in `main.c`.

## Test Signals
- A build with `CONFIG_B43_PHY_AC` should catch type/prototype drift, but runtime probe/start on AC hardware is the critical signal because missing callbacks are not compile-time errors.
- Any AC-PHY start attempt should be watched for null-function-pointer faults, failed PHY init, absent channel switching, and missing rfkill behavior.
