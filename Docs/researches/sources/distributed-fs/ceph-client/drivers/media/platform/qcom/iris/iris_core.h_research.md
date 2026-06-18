# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_core.h

## Purpose
`iris_core.h` defines the global Iris device/core structure and constants used by all instances and HFI code. It is the central object for hardware resources, V4L2 device registration, platform data, shared queues, command/response ops, power data, and firmware/core state.

## Important APIs, Types, And Functions
`enum domain_type` differentiates `ENCODER` and `DECODER`. `struct icc_info` describes interconnect bandwidth constraints. `struct iris_core` includes device and MMIO references, V4L2 devices and ioctl/vb2 ops, interconnect/clock/reset/power-domain resources, platform data, HFI queue memory, SFR memory, command/message/debug queue descriptors, lock, response buffer, HFI packet/header counters, command/response op tables, core completion, interrupt status, delayed system-error work, instance list, and decoded/encoded firmware capability arrays. Public functions are `iris_core_init()` and `iris_core_deinit()`.

## Control Flow
The core object is allocated and populated by probe/platform code outside this file. HFI generation setup installs `hfi_ops` and `hfi_response_ops`; runtime paths then use the same pointers for both system and session commands. IRQ handling uses `intr_status` and `response_packet`; session lookup walks `instances`.

## State And Persistence Behavior
The structure persists for the device lifetime. It holds long-lived hardware resource handles, runtime state, firmware capabilities copied from platform data, and shared memory pointers that are valid only while the core is initialized.

## Dependencies And Integration Points
The header includes HFI common/queue, platform, resources, and state headers. It is included by firmware, queue, command, response, power, VPU, decoder/encoder, and instance code. Platform data drives almost every core behavior: firmware name, PAS id, queue timeout, caps, buffer tables, UBWC config, and HFI parameter lists.

## Risks And Test Signals
Because `struct iris_core` is broadly shared, lock discipline is important. Tests should look for use-after-deinit of queue pointers, stale HFI ops, response buffer sizing against `IFACEQ_CORE_PKT_SIZE`, and correct capability arrays for encoder and decoder domains.
