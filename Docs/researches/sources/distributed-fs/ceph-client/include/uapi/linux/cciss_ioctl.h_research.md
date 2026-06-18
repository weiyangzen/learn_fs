
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/cciss_ioctl.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/cciss_ioctl.h

## Purpose
Defines the legacy CCISS userspace ioctl ABI for HP Smart Array controller management. It exposes controller information, interrupt coalescing, node name, heartbeat, bus/firmware/driver versions, passthrough commands, logical-volume info, and disk registration/rescan commands.

## APIs, Control Flow, and State
Important structures include `cciss_pci_info_struct`, `cciss_coalint_struct`, node/heartbeat/bus/firmware/driver typedefs, `IOCTL_Command_struct`, `BIG_IOCTL_Command_struct`, and `LogvolInfo_struct`. Ioctl numbers under `CCISS_IOC_MAGIC` include `CCISS_GETPCIINFO`, `GET/SETINTINFO`, `GET/SETNODENAME`, `GETHEARTBEAT`, `GETBUSTYPES`, `GETFIRMVER`, `GETDRIVVER`, `REVALIDVOLS`, `PASSTHRU`, `DEREGDISK`, `REGNEWDISK`, `REGNEWD`, `RESCANDISK`, `GETLUNINFO`, and `BIG_PASSTHRU`. Control flow is ioctl-dispatch based and may query firmware, submit CISS commands, or mutate logical disk registration. Persistent state includes controller settings, logical volume tables, and firmware command effects.

## Dependencies, Integration, Risks, and Tests
Depends on `linux/ioctl.h`, fixed-width types, and `cciss_defs.h`. Integration points are cciss character/block device management tools and SCSI/CISS passthrough. Risks include arbitrary passthrough command exposure, user buffer length validation, `MAX_KMALLOC_SIZE` assumptions, compat-layout drift, stale logical volume registration, and legacy tool dependence. Test signals include ioctl compat tests, passthrough read/write bounds tests, interrupt coalescing get/set, logical-volume info queries, rescan/register/deregister workflows, and permission checks around raw controller commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/cciss_ioctl.h -->
