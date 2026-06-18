## sources/distributed-fs/ceph-client/include/linux/coresight-pmu.h

Purpose: This header defines CoreSight ETM PMU naming and trace-ID encoding used by perf AUX hardware ID records.

Important APIs, types, and functions: `CORESIGHT_ETM_PMU_NAME` names the PMU as `cs_etm`. `CORESIGHT_LEGACY_CPU_TRACE_ID(cpu)` computes the historical per-CPU trace ID. AUX hardware ID masks include trace ID, sink ID, minor version, and major version fields. Version constants define major 0 and minor 1.

Control flow: Perf/CoreSight code packs and unpacks `PERF_RECORD_AUX_OUTPUT_HW_ID` payloads using the masks. Compatibility code may use the legacy CPU-to-trace-ID calculation for older kernels or tools.

State and persistence: Encoded AUX records persist in perf data files. The header stores no state but defines file-format interpretation bits.

Dependencies and integration points: It depends on bit mask helpers and integrates with perf tooling, CoreSight ETM drivers, sysfs sink IDs, and trace decoders.

Risks and test signals: Risks include breaking perf data compatibility, overlapping mask fields, wrong version interpretation, and legacy trace-ID mismatch. Test signals include perf record/report with CoreSight ETM, older-tool compatibility, sink ID decoding, and bitfield unit tests.
