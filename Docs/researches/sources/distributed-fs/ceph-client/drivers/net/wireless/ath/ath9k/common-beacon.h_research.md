# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/common-beacon.h

Purpose: Declares the shared beacon timer configuration APIs used by ath9k front-end code.

Important APIs/types: Forward declares `struct ath_beacon_config` and declares `ath9k_cmn_beacon_config_sta()`, `ath9k_cmn_beacon_config_adhoc()`, and `ath9k_cmn_beacon_config_ap()`.

Control flow: The header forms the compile-time contract between mode-specific beacon code and common timer math. Station callers pass an output `ath9k_beacon_state`; AP/IBSS callers mutate the beacon config and hardware interrupt mask through implementation side effects.

State/persistence: No direct state; all persistent state is in `ath_hw`, `ath_beacon_config`, and caller-provided timer structures.

Dependencies/integration: Included through `common.h` and consumed by `beacon.c` and shared ath9k code.

Risks: It has no include guard in this snapshot, relying on inclusion discipline. API users must respect TU/usec unit conversions performed by the implementation.

Test signals: Build coverage for all beacon modes and static analysis for duplicate inclusion or missing prototypes.
