# sources/distributed-fs/ceph-client/drivers/s390/cio/blacklist.c

Purpose: implements `cio_ignore=` and `/proc/cio_ignore` device blacklisting so selected s390 channel devices are hidden from Linux or re-enabled later.

Important APIs/types/functions: defines bitmap `bl_dev`, parser helpers `blacklist_range`, `pure_hex`, `parse_busid`, `blacklist_parse_parameters`, setup hook `blacklist_setup`, exported query `is_blacklisted`, proc write parser `blacklist_parse_proc_parameters`, seq operations for displaying ignored ranges, and proc init.

Control flow: boot parsing accepts comma-separated old-style devnos, full bus ids, ranges, `all`, `ipldev`, `condev`, and `!` inversion. It sets or clears per-SSID device bits. Proc writes accept `free`, `add`, or `purge`; freeing schedules conditional CSS evaluation for offline devices, and purge calls `ccw_purge_blacklisted`. Proc reads coalesce contiguous blacklisted devices into range output.

State and persistence: blacklist state is an in-memory bitmap covering each ssid/devno. It is initialized from boot parameters and mutable via procfs; not persisted across boot except via kernel command line.

Dependencies and integration: used by CIO subchannel validation through `is_blacklisted`; depends on IPL metadata, console devno, CSS evaluation, ccw purge, procfs/seq_file, and CIO debug logging.

Risks: parser validates cssid but only stores ssid/devno, consistent with this bitmap shape; invalid ranges return warnings at boot and EINVAL via proc. Proc input is capped at 64 KiB and trims trailing whitespace. Mutating blacklist while devices exist depends on CSS re-evaluation/purge behavior.

Test signals: command-line forms and inversions, `ipldev`/`condev` expansion, proc add/free/purge, range coalescing output across ssid boundaries, invalid bus ids/ranges, and device discovery behavior after freeing ignored devices.
