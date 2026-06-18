# sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/rp1-cfe/pisp-fe.h

Purpose: public interface for the RP1 PiSP Front End component.

Important APIs/types/functions: defines `enum pisp_fe_pads`, `struct pisp_fe_device`, and prototypes for ISR, config validation, job submission, start/stop, init, and uninit.

Control flow: no implementation; `cfe.c` calls these functions when scheduling FE jobs, dispatching interrupts, and managing stream lifecycle.

State and persistence: `pisp_fe_device` stores parent V4L2 device, MMIO base, hardware revision, in-frame count, media pads, and subdev.

Dependencies and integration: includes media/V4L2 subdev types and PiSP FE UAPI config definitions. The FE device is embedded in `struct cfe_device`.

Risks: pad enum indexes are used across CFE node descriptions, vb2 buffer arrays, and media links; changing them requires coordinated updates.

Test signals: build/link coverage and media graph validation that FE pads connect to expected CFE nodes.
