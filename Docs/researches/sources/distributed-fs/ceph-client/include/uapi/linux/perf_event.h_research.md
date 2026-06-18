# sources/distributed-fs/ceph-client/include/uapi/linux/perf_event.h

Purpose: Defines the `perf_event_open(2)` ABI, perf event attributes, ioctl controls, mmap metadata page, ring-buffer record formats, sample formats, branch and memory-data encodings, and related constants.

Important APIs/types/functions: Exports event type enums, hardware/software/cache IDs, sample format bits, branch sample bits, read formats, `PERF_ATTR_SIZE_VER*`, `struct perf_event_attr`, `struct perf_event_query_bpf`, perf ioctls, `struct perf_event_mmap_page`, `struct perf_event_header`, namespace link info, `enum perf_event_type`, ksymbol/BPF/cgroup/text-poke/AUX/callchain records, `union perf_mem_data_src`, memory hierarchy masks, `struct perf_branch_entry`, and `union perf_sample_weight`.

Control flow: Userspace fills `perf_event_attr` and calls `perf_event_open`, then controls the event fd through ioctls, reads counts, mmaps a metadata page plus data/AUX rings, and parses `perf_event_header` records. The kernel emits record layouts conditionally based on `sample_type`, `read_format`, `sample_id_all`, event flags, and mmap/AUX configuration.

State and persistence behavior: Event state is runtime kernel state: enabled/running time, PMU index/offset, ring buffer producer positions, AUX buffer positions, lost counts, BPF attachments, and sampling configuration. The mmap page exposes seqlock-protected metadata for user reads. No state is durable beyond event fd lifetime, though perf.data files persist decoded records.

Dependencies and integration points: Depends on `<linux/types.h>`, `<linux/ioctl.h>`, and `<asm/byteorder.h>`. Integrates with PMU drivers, tracepoints, kprobes/uprobes, BPF, cgroups, namespace reporting, AUX trace engines such as Intel PT/CoreSight, and perf tooling.

Risks: This is a dense forward-compatible ABI; `attr.size`, reserved bits, endianness-specific bitfields, ring-buffer memory ordering, sample layout conditionals, and compat struct handling are high risk. Raw sample payloads are explicitly not stable ABI. Permission controls must protect kernel, hypervisor, branch, register, and physical-address sampling data.

Test signals: Run `perf test`, open every event type, verify old `attr.size` versions, parse records with many `sample_type` combinations, test mmap ring and AUX overwrite modes, exercise BPF query/attach ioctls, run 32-bit compat tests, and validate memory data source and branch stack decoding on supported PMUs.
