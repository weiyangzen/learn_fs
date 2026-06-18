<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/misc/uacce/uacce.h -->
# sources/distributed-fs/ceph-client/include/uapi/misc/uacce/uacce.h

Purpose: defines common UACCE userspace accelerator queue ioctls, device flags, and queue file mmap region types.

Important APIs and types: `UACCE_CMD_START_Q` starts a queue and `UACCE_CMD_PUT_Q` stops/frees a queue before fd close. `UACCE_DEV_SVA` indicates Shared Virtual Addressing with PASID and device page fault support. `enum uacce_qfrt` distinguishes MMIO and device-user-share mmap regions.

Control flow, state, and persistence: userspace opens a UACCE queue file, maps regions, configures device-specific state, starts the queue, submits work, and uses PUT_Q or close to release resources. Queue state persists only for the queue fd lifetime.

Dependencies and integration points: integrates UACCE core, IOMMU SVA/PASID, accelerator device drivers, mmap, and device-specific headers such as HiSilicon QM.

Risks and test signals: risks include `BIT()` include assumptions, queue lifetime races, stale mmaps after PUT_Q, and SVA fault handling. Test start/put sequencing, mmap region offsets, SVA-capable and non-SVA devices, fd close cleanup, and concurrent queue users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/misc/uacce/uacce.h -->
