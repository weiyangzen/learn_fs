# sources/distributed-fs/ceph-client/tools/perf/util/arm-spe.h

Purpose: declares the Arm SPE perf integration contract and metadata layout used in AUXTRACE_INFO private data. It provides the shared constants needed by recording-side setup and decoding-side processing.

Important APIs and types: `ARM_SPE_PMU_NAME` identifies SPE PMUs by prefix. The first enum describes legacy v1 private fields, including PMU type and per-CPU mmap mode. The second enum describes v2 header fields: version, header size, shared PMU type, and CPU count. The third enum describes per-CPU metadata slots: magic, CPU logical id, parameter count, MIDR, PMU type, minimal interval, and event filter capability. Public functions are `arm_spe_recording_init()`, `arm_spe_process_auxtrace_info()`, and `arm_spe_pmu_default_config()`.

Control flow: this header does not implement control flow. It binds the recording side, which fills auxtrace info and default PMU config, to the decoding side in `arm-spe.c`, which validates and interprets the metadata.

State and persistence: the metadata enums define the stable serialized format stored inside perf.data AUXTRACE_INFO records. `ARM_SPE_HEADER_CURRENT_VERSION` is the current writer version and must remain compatible with the parser's legacy v1 detection.

Dependencies and integration points: forward declares perf event, session, and PMU types so Arm SPE can be conditionally integrated into perf record and report without exposing implementation internals.

Risks: enum order is ABI-like for perf.data files. Reordering or changing sizes would break older/newer perf interop. Additions need coordinated writer and reader changes, especially when heterogeneous CPU support needs new per-CPU parameters.

Test signals: perf.data compatibility tests should cover old v1 metadata, current v2 metadata with multiple CPUs, absent optional capability fields, and cross-version decode behavior.
