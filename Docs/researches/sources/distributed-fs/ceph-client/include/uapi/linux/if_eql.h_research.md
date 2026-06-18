<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_eql.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/if_eql.h

## Purpose
`if_eql.h` defines the ioctl ABI for the legacy equalizer load-balancer for serial network interfaces.

## Important APIs, types, and functions
Defaults include `EQL_DEFAULT_SLAVE_PRIORITY`, `EQL_DEFAULT_MAX_SLAVES`, `EQL_DEFAULT_MTU`, and `EQL_DEFAULT_RESCHED_IVAL`. Private ioctls include `EQL_ENSLAVE`, `EQL_EMANCIPATE`, `EQL_GETSLAVECFG`, `EQL_SETSLAVECFG`, `EQL_GETMASTRCFG`, and `EQL_SETMASTRCFG`. Structures are `master_config`, `slave_config`, and `slaving_request`, carrying max slaves, min/max/slave priority, and slave/master names.

## Control flow
User space configures an eql master interface, enslaves serial interfaces, adjusts master/slave priority parameters, and removes slaves through private netdevice ioctls. The driver schedules traffic across slaves according to priority and reschedule interval.

## State and persistence behavior
Master configuration, slave list, slave priorities, and MTU are live netdevice state. They persist only while the eql device exists unless restored by external configuration.

## Dependencies and integration points
It relies on private `SIOCDEVPRIVATE` ioctl numbering and integrates with netdevice ioctl paths and legacy serial/PPP-style network interfaces.

## Risks and test signals
Risks include obsolete driver coverage, private ioctl conflicts, name truncation, invalid priority ranges, and behavior under slave link failure. Test signals include ioctl get/set round trips, enslave/emancipate cycles, packet distribution tests, slave failure handling, and private ioctl compatibility checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_eql.h -->
