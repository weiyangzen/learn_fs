# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_device.c

Purpose: handles PowerVR device-level hardware initialization, register/clock setup, firmware loading, GPU ID validation, IRQ processing, feature exposure, and teardown.

Important APIs/functions: `pvr_device_init()` gets platform data, clocks, power ops, runtime PM, MMIO registers, GPU/firmware initialization, and IRQs. `pvr_device_fini()` tears down IRQ and GPU firmware state. `pvr_gpuid_decode_string()` parses a `B.V.N.C` override and is exported for KUnit. `pvr_device_has_uapi_quirk()`, `_enhancement()`, and `_feature()` expose filtered feature state. Internal helpers map registers, get clocks, process queue events, manage safety IRQs, request firmware, decode GPU ID registers, check supported BVNCs, set DMA mask, and initialize firmware/VM state.

Control flow and state: initialization powers the GPU before register access, loads firmware based on BVNC and major version, validates firmware-provided device info, chooses META/MIPS/RISC-V firmware processor, creates must-have stream masks, sets DMA info, creates kernel VM for non-MIPS firmware, initializes firmware, then requests threaded IRQ. IRQ handling clears firmware events, processes FWCCB, wakes KCCB waiters, processes active queues, marks runtime-PM activity, and handles RogueXE safety events.

Dependencies and integration: integrates platform devices, OF match data, clk, runtime PM, reset/power sequencing, firmware loader, pvr_fw, pvr_vm, pvr_queue, pvr_stream, DMA API, IRQs, and feature/quirk tables.

Risks: GPU support gating blocks unknown/experimental BVNCs unless `exp_hw_support` is set. Firmware filenames must match decoded BVNC. IRQ processing assumes firmware defs are initialized. Safety events are optional and feature-derived. Runtime PM ordering is critical around register access and firmware boot.

Test signals: probe/remove on supported DT compatibles, KUnit for GPU ID parsing, firmware load messages, IRQ-driven job completion, safety-event logs, and clean teardown without xarray/workqueue leaks.
