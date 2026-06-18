# sources/distributed-fs/ceph-client/include/uapi/linux/mmtimer.h

## Purpose
Defines Intel Multimedia Timer character-device ioctls for querying timer register offset, resolution, frequency, counter width, mmap availability, and current counter value.

## Important APIs, Types, And Functions
Exports ioctl base `MMTIMER_IOCTL_BASE` and ioctls `MMTIMER_GETOFFSET`, `MMTIMER_GETRES`, `MMTIMER_GETFREQ`, `MMTIMER_GETBITS`, `MMTIMER_MMAPAVAIL`, and `MMTIMER_GETCOUNTER`.

## Control Flow
Userspace issues required query ioctls to learn timing parameters, optionally maps registers if available, and reads counter values either through ioctl or mmap.

## State, Persistence, And Dependencies
State lives in hardware timer registers and driver implementation. No header dependencies are required.

## Integration Points
Used by legacy SGI/Intel multimedia timer applications and drivers exposing IA-PC multimedia timer-compatible devices.

## Risks
Some commands are optional, hardware may not safely support mmap, and return units differ: resolution is in femtoseconds while frequency is in Hz.

## Test Signals
Validate ioctl numbers, required-command support, nonzero frequency/resolution, counter monotonicity, mmap availability consistency, and graceful handling of unsupported offset queries.
