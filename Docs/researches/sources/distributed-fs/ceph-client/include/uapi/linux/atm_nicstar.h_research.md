<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atm_nicstar.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/atm_nicstar.h

## Purpose
Defines NICSTAR ATM driver-specific pool-statistics and buffer-level ioctls.

## Important APIs, Types, And Functions
Ioctls include `NS_GETPSTAT`, `NS_SETBUFLEV`, and `NS_ADJBUFLEV`. `buf_nr` contains min/init/max levels. `pool_levels` identifies buffer type, count, and levels. Buffer types include small, large, huge, and iovec.

## Control Flow
Utilities query pool stats, set level markers, or request automatic adjustment through SAR-private ioctls. `atmif_sioc` carries pointers to NICSTAR-specific data.

## State And Persistence
State is live NICSTAR receive/transmit pool configuration and counters; it is reset on driver/hardware reset.

## Dependencies And Integration Points
Depends on ATM API alignment and ioctl ranges. Integrates with NICSTAR driver diagnostics and buffer management.

## Risks And Edge Cases
The header notes external `sys/types.h` may be needed for some users. Invalid pool type/levels, count interpretation, and compat layout are risks.

## Test Signals
Pool stat reads, buffer level set/adjust tests, invalid type rejection, and stress under buffer pressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atm_nicstar.h -->
