# File Research: sources/block-storage/lvm2/lib/device/persist.c

This file implements LVM2 command-side persistent reservation orchestration for VG/PV devices. It parses `--setpersist` options, derives local PR keys from `local_pr_key` or `local_host_id`, reads SCSI/NVMe registrations/reservations, coordinates with `lvmpersist`, and keeps sanlock host-generation encoded keys synchronized.

Key responsibilities:
- Defines PR support checks in `dev_allow_pr`, accepting SCSI, multipath, and NVMe devices when NVMe support is compiled in.
- Maps SCSI persistent reservation types into internal `PR_TYPE_*` values, formats names such as `WE` and `WEAR`, and validates PR key strings as up to 16 hex digits.
- Maintains an optimization key file under `/var/lib/lvm/persist_key_<vg_name>_<vgid>`, with helpers to remove, rename, read, and write it. Sanlock VGs use the key file as a shortcut but fall back to device key discovery by host_id.
- Reads reservations and registered keys directly for SCSI devices with `SG_IO` persistent reserve-in commands. NVMe paths are delegated through `dev_read_reservation_nvme` and `dev_find_key_nvme` declared in `persist.h`.
- Normalizes multipath key discovery by sorting key arrays and removing duplicate keys reported through multiple paths.

The core state queries are `vg_is_registered`, `persist_is_started`, `persist_is_started_gen`, and `persist_is_started_by_other_hosts`. For non-shared VGs they expect a single local key and exclusive-style reservation. For shared/sanlock VGs they search for keys by `local_host_id`, accept WEAR shared reservation semantics, and validate sanlock generation bits when available. Partial registrations, inconsistent generations, read errors, missing reservations, and wrong reservation types are surfaced as errors or warnings depending on the caller's `may_fail` path.

Start/stop workflows are mostly wrappers around the external `lvmpersist` program:
- `persist_start` builds `lvmpersist start --ourkey ... --access ex|sh --vg ... --device ...` and optionally `--ptpl` or `--removekey`, then verifies every PV has the expected local key and a WE/WEAR reservation.
- `persist_stop`, `persist_stop_devs`, `persist_finish_before`, and `persist_finish_after` build stop commands and handle vgremove sequencing so PV lists are captured before metadata removal while the reservation is removed afterward.
- `persist_remove` and `persist_clear` invoke `lvmpersist remove` and `lvmpersist clear`.
- `persist_read` invokes `lvmpersist read` for all PV devices.

VG lifecycle integration:
- `persist_vgcreate_begin` starts an exclusive PR before PV initialization, using the raw configured key or host_id-derived key.
- `persist_vgcreate_update` converts a newly created shared VG from initial exclusive access to normal shared access, and for sanlock starts with generation 1.
- `persist_start_extend` starts PR on new PVs for local VGs, but for shared VGs requires all hosts to have pre-started PR on new devices and verifies new devices match existing registered keys.
- `persist_upgrade_ex` temporarily stops shared PR and restarts with exclusive access; `persist_upgrade_stop` stops a held upgraded key.

Sanlock-specific key handling is a major design point. Keys encode a fixed prefix, a 24-bit generation, and a 16-bit host_id. `get_our_key_sanlock_start` chooses the next generation from the running lockspace, key file, or devices. `persist_key_update` updates the registered key and key file after lockstart if sanlock reports a generation that differs from the guessed key. This avoids races where a rebooted host reuses an old key while another host removes it.

Important dependencies include `cmd_context`, `volume_group`, `pv_list`, `device`, device-type helpers from `dev-type.h`, config lookups from `config.h`, lvmlockd generation queries, endian conversion helpers, `exec_cmd`, and Linux SCSI generic headers. The file assumes command memory pools for short-lived arrays and uses explicit `malloc/free` for SG response buffers.

Edge cases and invariants:
- `setpersist_arg_flags` rejects contradictory option pairs such as `y,n` or `ptpl,noptpl`.
- Key-file corruption, parse failures, or host_id mismatches cause the key file to be removed and device discovery attempted.
- For exclusive starts, the file checks existing registered keys first to avoid starting a local VG already started by another host, especially on WEAR-capable multipath setups where device semantics alone may not enforce exclusivity.
- The key file is treated as an optimization; failure to write it generally logs but does not fail a successfully established PR.
