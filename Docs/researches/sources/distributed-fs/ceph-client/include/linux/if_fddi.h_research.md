# `sources/distributed-fs/ceph-client/include/linux/if_fddi.h`

Purpose: ANSI FDDI kernel statistics layout that augments generic netdevice stats with RFC 1512 SMT/MAC/path/port counters and state fields.

Important APIs/types/functions: `struct fddi_statistics`, containing `struct net_device_stats gen` plus station IDs, operation versions, MAC counters, neighbor addresses, frame/error counters, path configuration, and two-port status arrays.

Control flow and state: no functions. The structure is persistent driver/device statistics exported or queried by FDDI code.

Dependencies/integration: depends on netdevice and UAPI `if_fddi.h`; used by FDDI network drivers and ioctl/stat reporting paths.

Risks: fixed-size statistics layout must match legacy consumers; counters are 32-bit and can wrap; old FDDI paths may receive little active testing.

Test signals: FDDI driver build, statistics zero/init/update/export behavior, ioctl ABI size checks, and counter wrap handling where applicable.
