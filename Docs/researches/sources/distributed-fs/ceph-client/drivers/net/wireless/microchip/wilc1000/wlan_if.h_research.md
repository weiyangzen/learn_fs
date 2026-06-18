<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/wlan_if.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/wlan_if.h

## Purpose
This header defines the WILC firmware configuration interface: enums for firmware operating/security/power/scan/HT modes, bus wake/sleep acquisition policy, the generic `struct wid` request descriptor, and the large WID id namespace used for host-to-firmware configuration and firmware-to-host status.

## Important APIs, Types, And Functions
Important enums cover BSS type, 11g mode, preamble, active/passive scan, power-save mode, bus acquire/release behavior, security bit composition, authentication type, MFP policy, site survey mode, ACK policy, rekey policy, scan filters, 11n protection/operation/SMPS, TX rates, scan request type, management frame registration indexes, and WID wire types. `struct wid` is the common descriptor used by `wilc_send_config_pkt()` callers.

The WID list maps typed ids for basic MAC settings, counters, strings, keys, association data, PMKID, remain-on-channel, external authentication, station/AP management, multicast filter, and firmware/hardware metadata.

## Control Flow
This header does not execute code. Its values drive config packet assembly in `wlan.c`/`wlan_cfg.c` and higher cfg80211 operations that translate Linux wireless requests into firmware WID set/get sequences.

## State And Persistence
The enums and WID ids describe firmware-persistent settings such as BSS type, channel, security mode, keys, beacon interval, retry limits, power-save mode, multicast filters, and station entries. On the host side, `struct wid` values are transient request descriptors and selected responses are cached by `struct wilc_cfg`.

## Dependencies And Integration Points
Includes Linux netdevice definitions and WILC firmware helpers from `fw.h`. It is consumed by WILC cfg80211, host-interface, core config, and data-path files. It is the main symbolic bridge between Linux cfg80211 concepts and Microchip firmware WID commands.

## Risks
WID ids are firmware ABI; changing values or types breaks device configuration. Security enums combine bit flags in firmware-specific ways and must match key/install code. The type nibble is used by generic serialization, so an incorrectly typed WID will produce malformed packets. Several ids are custom or sparsely documented, increasing compatibility risk across firmware versions.

## Test Signals
Validation should cover connect/AP/key/scan/ROC/external-auth/multicast workflows that exercise diverse WIDs, plus explicit get/set tests for each WID type. Firmware logs and config reply parsing should be watched for unsupported or malformed WID errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/wlan_if.h -->
