<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/perf_event.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/perf_event.h

Purpose: this is the core Linux `perf_event_open(2)` UAPI definition. It supplies event type IDs, sample/read formats, `struct perf_event_attr`, mmap metadata layout, record stream formats, ioctls, memory data-source encodings, branch records, and constants used by perf tools and trace consumers.

Important APIs/types: key surfaces are `enum perf_type_id`, hardware/software/cache event enums, `enum perf_event_sample_format`, branch sampling masks, `enum perf_event_read_format`, `struct perf_event_attr`, `struct perf_event_mmap_page`, `struct perf_event_header`, `enum perf_event_type`, `union perf_mem_data_src`, `struct perf_branch_entry`, and `union perf_sample_weight`. The `PERF_ATTR_SIZE_VER*` constants are critical for forward/backward compatibility. Ioctls such as `PERF_EVENT_IOC_ENABLE`, `DISABLE`, `RESET`, `PERIOD`, `SET_FILTER`, `SET_BPF`, `QUERY_BPF`, and `MODIFY_ATTRIBUTES` define the fd control plane.

Control flow: userspace fills `perf_event_attr`, opens an event fd, optionally mmaps the metadata/ring pages, controls the event with ioctls, reads grouped counter formats, and parses `PERF_RECORD_*` records according to enabled `sample_type` and `sample_id_all` bits. The mmap page includes seqlock-style fields for lockless user reads and AUX ring-buffer coordinates for hardware trace.

State and persistence: kernel event state persists while fds are open. Ring-buffer contents, counter values, lost counts, AUX watermarks, and enable/running times are live kernel/user shared state. ABI state is mostly append-only; consumers must honor `attr.size`, `header.size`, feature bits, endianness, and optional fields.

Dependencies/integration: included by perf, BPF tracing tools, KVM tooling, profilers, and observability agents. It depends on fixed-width Linux types, ioctl macros, and architecture byte-order definitions. In this subset, `tools/kvm/kvm_stat/kvm_stat` mirrors a small `perf_event_attr` subset and uses tracepoint events plus group reads.

Risks and test signals: high-risk areas are struct packing, bitfield endianness, ring-buffer ordering, interpreting optional sample payloads, 32-bit vs 64-bit truncation, and older-kernel attr sizes. Good tests open tracepoint/software events, exercise grouped reads, mmap records, lost-sample accounting, branch/data-source samples, BPF query paths, and parser tolerance for unknown `PERF_RECORD_*` types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/perf_event.h -->
