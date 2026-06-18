# sources/distributed-fs/ceph-client/include/uapi/linux/npcm-video.h

Purpose: Defines the userspace V4L2 control ABI for the Nuvoton NPCM video capture/differentiation engine.

Important APIs/types/functions: Exports `V4L2_CID_NPCM_CAPTURE_MODE`, `enum v4l2_npcm_capture_mode`, `V4L2_NPCM_CAPTURE_MODE_COMPLETE`, `V4L2_NPCM_CAPTURE_MODE_DIFF`, and `V4L2_CID_NPCM_RECT_COUNT`. The controls are based on `V4L2_CID_USER_NPCM_BASE` from `<linux/v4l2-controls.h>`.

Control flow: This header has no executable flow. Userspace sets the capture mode control through V4L2 ioctls; the driver interprets complete mode as capture of a full frame and diff mode as comparison against the previous in-memory frame. Userspace reads the rectangle count control to learn how many HEXTILE rectangles the compressed result contains.

State and persistence behavior: The header defines only ABI constants. Runtime state lives in the NPCM V4L2 driver and hardware frame buffers; complete mode normally reports one rectangle, while diff mode reports the current differentiated frame rectangle count.

Dependencies and integration points: Integrates with V4L2 control enumeration, `v4l2-ctl`, media userspace, and the NPCM driver documentation referenced by the comments. It is not Ceph-specific; this source tree vendors the Linux kernel UAPI set.

Risks: Control ID drift would break userspace control discovery. Incorrect mode handling can make userspace interpret full-frame output as differential rectangles or vice versa. Rectangle count must be synchronized with the frame returned by the driver.

Test signals: Compile UAPI consumers, enumerate controls via V4L2, set both capture modes, capture complete and diff frames, and verify rectangle counts and HEXTILE output match driver documentation.
