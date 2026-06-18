# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/perf_event_sample_period.c

Purpose: validates direct reads from `bpf_perf_event_data->sample_period` for all supported access widths.

Important APIs/types/functions: uses `BPF_LDX_MEM` from `struct bpf_perf_event_data`, `offsetof(..., sample_period)`, and `BPF_PROG_TYPE_PERF_EVENT`.

Control flow: four tests load byte, halfword, word, and doubleword values from the `sample_period` context field, then exit.

State and persistence behavior: no persistent state. The relevant verifier state is context-field read permission and width handling for perf event programs.

Dependencies and integration points: must be loaded as `BPF_PROG_TYPE_PERF_EVENT`; relies on the perf-event context ABI.

Risks: context access table drift could reject valid observability programs or allow invalid partial accesses elsewhere.

Test signals: all four cases accept for `BPF_PROG_TYPE_PERF_EVENT`.
