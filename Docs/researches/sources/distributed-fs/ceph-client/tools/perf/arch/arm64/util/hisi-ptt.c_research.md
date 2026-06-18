# sources/distributed-fs/ceph-client/tools/perf/arch/arm64/util/hisi-ptt.c

Purpose: HiSilicon PTT perf auxtrace recorder for PCIe trace data.

Important APIs/types/functions: `hisi_ptt_info_priv_size`, `hisi_ptt_info_fill`, `hisi_ptt_set_auxtrace_mmap_page`, `hisi_ptt_recording_options`, `hisi_ptt_reference`, `hisi_ptt_recording_free`, `KiB`, `MiB`, `hisi_ptt_recording`, `auxtrace_record`.

Control flow: Finds a single PTT PMU event, forces period sampling, configures AUX mmap defaults, moves the event to the front, adds a dummy tracking event, and fills auxtrace info.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on perf auxtrace, HiSilicon PTT PMU definitions, TSC reference, page-size and paranoid checks.

Risks: Code assumes a matching event before `evlist__to_front`; multiple PTT events are rejected; AUX size must be power-of-two.

Test signals: PTT record with one event, duplicate events, missing PMU, invalid mmap sizes, and report decoder metadata.

Source coverage: researched from the complete local file (189 lines, 4743 bytes).
