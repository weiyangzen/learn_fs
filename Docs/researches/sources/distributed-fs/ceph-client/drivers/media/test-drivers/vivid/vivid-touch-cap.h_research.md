# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-touch-cap.h

Purpose: defines touch dimensions, pressure/pattern constants, gesture enum values, queue operations, and touch ioctl/generator declarations.

Important APIs and types: constants include `VIVID_TCH_HEIGHT`, `VIVID_TCH_WIDTH`, pressure limits, sequence/pattern counts, and `enum vivid_tch_test`. Public APIs cover touch format/input/streamparm operations, `vivid_fillbuff_tch`, `vivid_set_touch`, and `vivid_touch_cap_qops`.

Control flow: core setup initializes the touch format through `vivid_set_touch`; queue and ioctl tables use the declared operations.

State and persistence: no header-owned state. Constants define the ABI-visible buffer dimensions and gesture cycle.

Dependencies and integration points: consumers need V4L2/vb2 types and Vivid core declarations.

Risks: changing width/height or pressure constants changes userspace-visible touch buffer shape and expected gesture output.

Test signals: compile coverage plus touch format and buffer-size validation tests cover this header.
