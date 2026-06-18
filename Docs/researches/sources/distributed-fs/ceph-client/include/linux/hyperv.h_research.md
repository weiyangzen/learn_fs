# sources/distributed-fs/ceph-client/include/linux/hyperv.h

## Purpose
Defines Linux Hyper-V VMBus ABI structures, ring-buffer helpers, channel/device/driver state, GPADL packet formats, integration component messages, and public VMBus helper APIs.

## APIs, Control Flow, and State
Core state includes packed GPADL descriptors, `struct hv_ring_buffer`, `struct hv_ring_buffer_info`, VMBus channel offer/message structures, `struct vmbus_requestor`, `struct vmbus_channel`, `struct hv_driver`, and `struct hv_device`. Ring flow uses read/write indices, interrupt masks, pending-send-size flow control, `hv_begin_read()`/`hv_end_read()` barriers, and packet iterators. Channel flow negotiates VMBus version, accepts offers, opens channels with ring-buffer GPADLs, sends packets or GPA-direct buffers, receives packets, tears down GPADLs, changes target CPU, and closes channels. Persistent state lives in channel lists, ring pages, GPADL handles, request bitmaps, callback/tasklet/work objects, sysfs/debugfs objects, per-channel state, feature flags, and statistics counters.

## Dependencies, Integration, Risks, and Tests
Depends on Hyper-V UAPI/HVHDK definitions, memory management, scatterlists, device model, interrupts, timers, workqueues, GUIDs, PCI, DMA, and reciprocal division. Integrates with VMBus drivers for storage/network/video/KVP/time/heartbeat/hvsock/PCI and with confidential-computing paravisor flags for encrypted ring/external memory. Risks include packed ABI layout drift, ring index races, missing memory barriers, request ID reuse, rescind/open/close races, wrong GPADL page accounting when `PAGE_SIZE != HV_HYP_PAGE_SIZE`, and a suspicious `VMPACKET_TRANSFER_MODE()` cast to undefined `struct IMPACT`. Test signals include Hyper-V channel negotiation, ring wraparound and full-ring flow-control tests, GPADL establish/teardown, packet iterator tests, rescind stress, hvsock subchannel tests, and build checks for packet macros.
