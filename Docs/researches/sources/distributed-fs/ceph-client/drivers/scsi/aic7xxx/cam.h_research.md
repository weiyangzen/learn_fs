# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/cam.h

Purpose: Linux-port compatibility header for FreeBSD CAM status, async notification, and data-direction values used by aic7xxx/aic79xx driver code.

Important APIs/types/functions: `cam_status` enumerates request completion, abort, timeout, SCSI status, queue freeze, requeue, and host/bus error codes. `ac_code` enumerates asynchronous events such as device found/lost, bus reset, transfer negotiation, and inquiry changes. `ccb_flags` maps CAM transfer directions onto Linux DMA constants.

Control flow: no runtime flow; constants are consumed by driver logic that was originally structured around CAM status names.

State and persistence: no mutable state. Status values are compiled into command-completion and error-handling paths.

Dependencies and integration: includes `<linux/types.h>` and depends on Linux DMA direction constants. It integrates legacy CAM naming with Linux SCSI midlayer behavior in surrounding aic driver files.

Risks and test signals: semantic drift between CAM names and Linux SCSI error handling can cause incorrect queueing or retry behavior if callers assume FreeBSD semantics. Regression signals are command timeout handling, queue-freeze/requeue cases, bus reset notifications, and transfer-negotiation event paths in aic7xxx/aic79xx.
