<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/hisi-ptt.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/hisi-ptt.h

## Purpose
`hisi-ptt.h` declares the public hooks and constants for HiSilicon PTT perf support.

## Important APIs, types, and functions
It defines `HISI_PTT_PMU_NAME` as `"hisi_ptt"` and `HISI_PTT_AUXTRACE_PRIV_SIZE` as one `u64`. It declares `hisi_ptt_recording_init` for record-side setup and `hisi_ptt_process_auxtrace_info` for report/session-side auxtrace setup.

## Control flow
Record code can initialize an auxtrace recorder for the `hisi_ptt` PMU. Read/report code calls `hisi_ptt_process_auxtrace_info` when an AUXTRACE_INFO event of this type is encountered.

## State and persistence
The private AUXTRACE payload contract is one `u64`, currently used by `hisi-ptt.c` as the PMU type.

## Dependencies and integration points
The declarations depend on perf PMU, auxtrace record, perf event, and perf session types supplied by including translation units. The header links record and report sides of HiSilicon PTT support.

## Risks
Only a minimal private data size is specified; future extensions must preserve compatibility. The header does not forward-declare all referenced structs itself, so include ordering matters unless callers already include perf core headers.

## Test signals
Build record/report configurations with HiSilicon PTT enabled, validate AUXTRACE private size, and test both PMU-name discovery and auxtrace-info processing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/hisi-ptt.h -->
