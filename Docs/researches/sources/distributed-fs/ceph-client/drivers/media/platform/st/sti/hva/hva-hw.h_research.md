# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/hva/hva-hw.h

Purpose: declares the HVA hardware support interface and command identifiers used by encoder backends and the V4L2 platform layer.

Important APIs and types: defines hardware version constants `HVA_VERSION_UNKNOWN` and `HVA_VERSION_V400`, `enum hva_hw_cmd_type` with `H264_ENC` plus client/all freeze/start/remove commands, and prototypes for probe/remove, runtime PM, task execution, and debugfs register dumping.

Control flow: V4L2 probe calls `hva_hw_probe`, PM hooks delegate to runtime suspend/resume, codec backends call `hva_hw_execute_task` with a DMA task descriptor, and remove calls `hva_hw_remove`.

State and persistence: no header-owned state. The API mutates `struct hva_dev` and `struct hva_ctx` state in the implementation.

Dependencies and integration points: includes `hva-mem.h` for `struct hva_buffer` and requires `struct platform_device`, `struct device`, `struct hva_dev`, and `struct hva_ctx` visibility from including files. It is consumed by `hva-h264.c`, `hva-debugfs.c`, and the V4L2 core.

Risks: command IDs are hardware ABI values. Unsupported command enum members are declared, but `hva_hw_execute_task` currently handles only `H264_ENC`; callers must not assume all enum values are implemented.

Test signals: compile coverage, H.264 task submission through `hva_h264_encode`, and debugfs register dump availability when `CONFIG_VIDEO_STI_HVA_DEBUGFS` is enabled.
