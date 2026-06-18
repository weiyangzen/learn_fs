# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_vlan_mode.c

## Purpose
Determines, sets, and caches the device VLAN mode. It negotiates double VLAN mode support with DDP package metadata and firmware, programs DVM/SVM through admin queue commands, updates default switch recipes for DVM, and performs post-DDP-download mode-specific configuration.

## Important APIs and Functions
- `ice_set_vlan_mode()` attempts DVM when both package and firmware support it, falling back to SVM if DVM setup fails.
- `ice_is_dvm_ena()` returns cached `hw->dvm_ena`.
- `ice_post_pkg_dwnld_vlan_mode_cfg()` caches mode after package download and switches parser proto IDs to DVM or logs why QinQ is unavailable.
- `ice_pkg_get_supported_vlan_mode()` reads package metadata section `ICE_SID_RXPARSER_METADATA_INIT`.
- `ice_aq_get_vlan_mode()` and `ice_aq_set_vlan_mode()` wrap AQ opcodes 0x020D/0x020C.
- `ice_set_dvm()` programs DVM AQ parameters, updates default recipes, sets port params, and installs DVM boost entries.
- `ice_set_svm()` programs SVM port and VLAN mode parameters.

## Control Flow
DVM support requires both package support and firmware AQ support. If unsupported, `ice_set_vlan_mode()` leaves the device in SVM-compatible behavior. DVM setup has multiple hardware-programming stages; any failure falls back to `ice_set_svm()`. After DDP download, all PFs call post configuration because only one PF performed package download under the global config lock.

## State and Persistence
The device VLAN mode is hardware/firmware configuration and is not dynamically changed during runtime. `hw->dvm_ena` caches the result for fast operation-table and VLAN behavior decisions. DVM modifies switch recipes and parser/protocol behavior globally.

## Dependencies and Integration Points
Depends on `ice_common.h`, package buffer/AQ helpers, metadata section constants, recipe update APIs, port parameter AQ, boost TCAM setup, and parser protocol mutation. VSI/VF VLAN ops consult `ice_is_dvm_ena()`.

## Risks
- DVM setup changes default recipe lookup indices and packet flag masks; errors can affect VLAN filtering and promiscuous matching globally.
- AQ validation rejects invalid priority tagging, RDMA packet flag, or management protocol ID fields.
- The fallback to SVM hides DVM failure from callers except debug logs; feature-level tests must confirm actual cached mode.
- `ice_post_pkg_dwnld_vlan_mode_cfg()` prints user guidance by probing support again, which repeats AQ/package reads.

## Test Signals
Test package-only support missing, firmware-only support missing, successful DVM, DVM AQ/recipe/port/boost failure falling back to SVM, cached `hw->dvm_ena`, QinQ availability messaging, and VLAN filtering/promisc behavior after recipe updates.
