# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/debugfs.c

## Purpose

`debugfs.c` creates MLD debugfs controls and diagnostics for firmware restart/NMI, echo commands, HE sniffer configuration, TAS status, 6 GHz BIOS policy, packet injection, thermal CTDP, max sleep, PTP timestamping, per-vif power/beacon/low-latency/TWT/internal-MLO-scan controls, AP beacon IE injection, and per-link-station rate/TLC debug commands.

## Important APIs, Types, and Functions

Public registration functions are `iwl_mld_add_debugfs_files()`, `iwl_mld_add_vif_debugfs()`, `iwl_mld_add_link_debugfs()`, and `iwl_mld_add_link_sta_debugfs()`. Important handlers include `iwl_dbgfs_fw_nmi_write()`, `iwl_dbgfs_fw_restart_write()`, `iwl_dbgfs_send_echo_cmd_write()`, `iwl_dbgfs_he_sniffer_params_*()`, `iwl_dbgfs_tas_get_status_read()`, `iwl_dbgfs_wifi_6e_enable_read()`, `iwl_dbgfs_inject_packet_write()`, VIF power/beacon-filter/low-latency handlers, beacon IE injection/restore, TWT setup/operation, internal MLO scan, fixed rate, and TLC DHC.

## Control Flow

Registration adds top-level files under the device debugfs directory, symlinks into mac80211 debugfs, then adds per-vif/per-link/per-link-station directories as mac80211 objects appear. Most write handlers parse user input, reject commands when firmware is stopped or in D3, then send firmware commands or mutate driver debug state under `wiphy_locked_debugfs_*` wrappers. Packet injection hex-decodes an RX packet into a temporary page and calls the MLD RX path with BH disabled.

## State and Persistence Behavior

Debugfs writes can deliberately change runtime state: trigger firmware errors, set `do_not_dump_once`, change monitor AID/BSSID, clear firmware monitor buffers, alter beacon filter and low-latency flags, inject AP beacon IEs, configure TWT, start/stop internal scans, force rates, and update `debug_max_sleep`/`monitor.ptp_time`.

## Dependencies and Integration Points

The file uses MLD hcmd, iface, station, TLC, power, notification, AP, scan, thermal, DHC/RFI/TAS firmware APIs, DMI, hex decoding, debugfs, mac80211 debugfs object lifetimes, and the wrapper macros from `debugfs.h`.

## Risks and Edge Cases

Many handlers are intentionally dangerous and should remain debug-only: firmware NMI/restart, RX injection, beacon injection, TWT override, and fixed-rate commands can disrupt live traffic. Buffer-size macros cap input/output but parsing must stay synchronized with wrapper sizes. `iwl_mld_dbgfs_fw_cmd_disabled()` prevents commands while stopped or in D3, but state-only knobs can still affect later behavior. Beacon IE injection toggles `extra_beacon_tailroom` and must restore it even on errors.

## Test Signals

Build with debugfs, thermal, and PM variants. Validate each file appears in the right top-level/vif/link-sta directory, bad input returns `-EINVAL`, firmware-disabled paths return `-EIO`, TAS read handles invalid firmware responses, packet injection rejects malformed packets, beacon IE restore re-enables normal templates, and symlinks are valid.
