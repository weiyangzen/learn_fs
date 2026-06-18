# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/ahb.h

## Purpose
`ath12k/ahb.h` declares the AHB-private state, firmware/remoteproc constants, userPD IRQ IDs, family-operation interfaces, and register/unregister entry points used by ath12k AHB platform support.

## Important APIs, Types, And Constants
- Timeout and firmware constants include rootPD ready, userPD spawn/ready/stop, recovery, firmware prefix/suffix, secondary firmware name, PAS SWID, userPD ID mask, and firmware-name length.
- `enum ath12k_ahb_smp2p_msg_id` names power-save enter/exit messages; `enum ath12k_ahb_userpd_irq` indexes spawn, ready, and stop-ack IRQs.
- `struct ath12k_ahb_device_family_ops` lets device-family code provide `probe`, `arch_init`, and `arch_deinit`.
- `struct ath12k_ahb` stores `ath12k_base`, target remoteproc, XO clock, rootPD notifier/completion, SMEM spawn/stop state, userPD completions/IRQs, userPD ID, family ops, and SCM authentication state.
- `struct ath12k_ahb_driver` packages family name, OF match table, family ops, and embedded `platform_driver`.
- `ath12k_ab_to_ahb()` converts `ab->drv_priv` to AHB-private state.
- `ath12k_ahb_register_driver()` and `ath12k_ahb_unregister_driver()` expose the family driver registry.

## Control Flow And State Behavior
The header has no executable flow except `ath12k_ab_to_ahb()`. Its structures are allocated as driver-private data by `ath12k_core_alloc()` in `ahb.c`, initialized during probe, mutated during remoteproc/userPD boot and shutdown, and cleared by core/resource teardown.

## Dependencies And Integration Points
It includes clock, Qualcomm remoteproc, platform device, and ath12k core headers. It is shared between the common AHB backend and device-family implementations, including Wi-Fi 7 family code under the ath12k tree.

## Risks And Edge Cases
- The private structure is accessed through a cast from `ab->drv_priv`, so allocation size and bus type must match the AHB backend.
- Timeout constants control probe/power behavior on real firmware; too-short values can cause false boot failures.
- The header references `struct ath12k_ahb_ops *ahb_ops`, but the visible file set does not define or use that type here, so it may be legacy or for external family code.
- UserPD ID and PAS ID bit encodings must match firmware/SCM expectations.

## Test Signals
Compile AHB-enabled builds, validate family driver registration for each supported `ath12k_device_family`, verify `ath12k_ab_to_ahb()` private-data sizing, test userPD IRQ array indexing, and exercise timeout constants through boot/stop paths on hardware.
