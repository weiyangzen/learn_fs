<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ptp_clock.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/ptp_clock.h

Purpose: defines the Precision Time Protocol hardware clock character-device ABI for capabilities, external timestamping, periodic output, PPS, pin muxing, and system/device time offset measurement.

Important APIs and types: flag definitions cover external timestamp edges/offsets/strict validation and periodic output one-shot/duty-cycle/phase modes. `struct ptp_clock_time`, `ptp_clock_caps`, `ptp_extts_request`, `ptp_perout_request`, `ptp_sys_offset`, `ptp_sys_offset_extended`, `ptp_sys_offset_precise`, `ptp_pin_desc`, and `ptp_extts_event` define ioctl/event payloads. Ioctls include v1 and strict v2 variants for get caps, external timestamp, periodic output, PPS enable, sys offset, pin get/set, precise/extended offset, mask controls, and cycle-based offset queries.

Control flow: userspace opens `/dev/ptpN`, queries capabilities, configures timestamp or output channels/pins, reads events, and measures PHC-system offset. The kernel validates flags, programs hardware through PTP clock drivers, and returns timestamp samples.

State and persistence: PTP state is per hardware clock: configured pins, external timestamp channels, periodic outputs, PPS enablement, masks, and driver counters. It is runtime hardware state, not persistent across driver reset.

Dependencies and integration points: depends on Linux ioctl/types and `__kernel_clockid_t`. Integrates with network drivers, PHC subsystem, PPS, time synchronization daemons such as linuxptp/chrony, hardware timestamping, and time-aware networking.

Risks and test signals: risks include nanosecond/second sign semantics, flag compatibility between v1/v2 ioctls, sample count bounds, clockid reserved-field compatibility, pin/channel validation, and hardware capability mismatches. Test `phc2sys`/`testptp`, ext timestamp edges, perout duty/phase, sys offset sample limits, pin muxing, PPS enable, and invalid flag rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ptp_clock.h -->
