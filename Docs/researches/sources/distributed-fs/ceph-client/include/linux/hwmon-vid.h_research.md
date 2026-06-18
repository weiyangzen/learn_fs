# sources/distributed-fs/ceph-client/include/linux/hwmon-vid.h

## Purpose
Declares VID/VRM voltage conversion helpers for hwmon drivers.

## APIs, Control Flow, and State
`vid_from_reg()` and `vid_which_vrm()` are implemented elsewhere. Inline `vid_to_reg()` converts millivolts to a VID code for VRM 9.0/9.1 only, returning `-EINVAL` for unsupported VRM revisions or `-1` for voltages outside 1100-1850 mV. The conversion is integer-only and avoids floating point. There is no persistent state.

## Dependencies, Integration, Risks, and Tests
Depends on errno definitions through common include context and `u8`. Integrates with older voltage regulator/sensor hwmon drivers. Risks are unsupported VRM revisions, millivolt vs volt unit confusion, and callers not distinguishing `-EINVAL` from out-of-range `-1`. Test signals include known VID/voltage conversion vectors and hwmon sensor output checks for legacy boards.
