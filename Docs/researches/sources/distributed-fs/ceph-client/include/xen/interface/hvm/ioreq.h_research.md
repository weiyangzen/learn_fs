# sources/distributed-fs/ceph-client/include/xen/interface/hvm/ioreq.h

Purpose: defines the HVM I/O request record shared between Xen and a device model for PIO, MMIO copy, PCI config, time offset, and mapcache invalidation exits.

Important APIs/types/functions: request direction constants `IOREQ_READ` and `IOREQ_WRITE`; states `STATE_IOREQ_NONE`, `STATE_IOREQ_READY`, `STATE_IOREQ_INPROCESS`, `STATE_IORESP_READY`; request types `IOREQ_TYPE_PIO`, `IOREQ_TYPE_COPY`, `IOREQ_TYPE_PCI_CONFIG`, `IOREQ_TYPE_TIMEOFFSET`, and `IOREQ_TYPE_INVALIDATE`; and `struct ioreq`.

Control flow: Xen fills an `ioreq`, sets state ready, and notifies the device model through the `vp_eport` event channel. The device model decodes `addr`, `data`, `count`, `size`, `dir`, `type`, and `data_is_ptr`, services the emulated I/O, writes any response data, and advances state to response ready.

State and persistence: `state` is the synchronization point for each request. The record lives in shared I/O request pages configured by HVM params or newer DMOP paths.

Dependencies and integration points: consumed by QEMU or other Xen HVM device models, HVM param setup (`HVM_PARAM_IOREQ_PFN`, `HVM_PARAM_BUFIOREQ_PFN`), PCI config emulation, MMIO handlers, and mapcache invalidation.

Risks: bitfield layout and endian assumptions are ABI-sensitive. PCI config address encoding packs segment/bus/device/function/offset into `addr`; incorrect decoding targets the wrong device. `data_is_ptr` requires safe guest physical memory access.

Test signals: device-model integration tests for PIO/MMIO reads and writes, PCI config cycles, repeated-string `count` handling, event-channel notification, and state-machine races under concurrent vCPU exits.
