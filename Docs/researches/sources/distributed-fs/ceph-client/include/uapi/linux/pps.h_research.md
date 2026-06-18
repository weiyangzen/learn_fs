<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/pps.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/pps.h

Purpose: defines the Pulse-Per-Second userspace ABI for querying PPS sources, configuring capture modes, fetching timestamp events, and creating PPS clients.

Important APIs and types: mode bits include capture assert/clear, offset assert/clear, echo assert/clear, canonical/noncanonical timestamp formats, and read/write wait modes. `struct pps_ktime`, `pps_kparams`, `pps_fdata`, `pps_bind_args`, and `pps_info` carry timestamps, offsets, sequence counters, source metadata, and binding information. `PPS_GETPARAMS`, `PPS_SETPARAMS`, `PPS_GETCAP`, `PPS_FETCH`, `PPS_KC_BIND`, and related ioctls form the API.

Control flow: userspace opens a PPS device, queries capabilities, sets desired capture/offset mode, waits/fetches events, and optionally binds kernel consumers. The kernel timestamps assert/clear edges and updates sequence counters.

State and persistence: PPS source state is runtime only: current params, last assert/clear timestamps, sequence counters, and source path/name. Offsets and modes persist for the device open/source lifetime, not across reboot.

Dependencies and integration points: depends on Linux types and ioctl. Integrates with serial/GPIO/PTP PPS providers, NTP/chrony time synchronization, and kernel PPS clients.

Risks and test signals: risks include timestamp format compatibility, timeout semantics, sequence wrap, offset sign handling, and capability/mode mismatch. Test PPS_FETCH blocking and timeout paths, assert/clear modes, offsets, compat structs, and NTP/chrony integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/pps.h -->
