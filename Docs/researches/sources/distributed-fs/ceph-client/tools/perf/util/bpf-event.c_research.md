# sources/distributed-fs/ceph-client/tools/perf/util/bpf-event.c

Purpose: synthesizes and processes perf records that describe BPF programs, BPF ksymbols, BTF data, and optional BPF metadata. This lets perf annotate and symbolize BPF JIT code in recorded sessions and sideband streams.

Important APIs and functions: `machine__process_bpf()` handles runtime `PERF_RECORD_BPF_EVENT` records and marks kernel maps as BPF program DSOs. `perf_event__synthesize_bpf_events()` enumerates kernel BPF programs, creates `PERF_RECORD_KSYMBOL` and `PERF_RECORD_BPF_EVENT` records, and synthesizes BPF trampoline/dispatcher images from kallsyms. `evlist__add_bpf_sb_event()` installs a dummy sideband event with `bpf_event` enabled. `__bpf_event__print_bpf_prog_info()` prints stored BPF program details. Metadata helpers read `.rodata` BPF maps with BTF and emit `PERF_RECORD_BPF_METADATA` when supported.

Control flow: synthesis obtains program ids with `bpf_prog_get_next_id()`, opens each program fd, linearizes selected `bpf_prog_info` arrays through `get_bpf_prog_info_linear()`, optionally loads BTF, emits a ksymbol per JITed subprogram, inserts program info into `perf_env`, emits BPF load events, and emits metadata records. Sideband events call `perf_env__add_bpf_info()` when load records arrive. Processing BPF load records later finds stored info and associates matching kernel maps with BPF metadata.

State and persistence: BPF program info and BTF blobs are stored in `perf_env` as `bpf_prog_info_node` and `btf_node`, making them available for later report/annotation. Metadata allocation owns per-subprogram names and event payload until synthesized or freed. Unload events intentionally do not free program info because annotation can still need it later.

Dependencies and integration points: uses libbpf, kernel BPF syscalls, perf env/session/machine/map/DSO APIs, kallsyms, synthetic event delivery, `bpf-utils` linearization, and optional libbpf string formatting support.

Risks: kernel support is feature-dependent; old kernels can lack program info fields, BTF, BPF event sideband, or permissions. Subprogram counts must match across ksyms, lengths, tags, and function info. Metadata path assumes `.rodata` array maps with BTF datasec layout and may silently skip unsupported maps. Error handling often downgrades old-kernel/permission failures to nonfatal behavior, so missing BPF symbolization can be quiet.

Test signals: record/report tests with single and multi-subprogram BPF programs, with and without BTF, with metadata variables, old-kernel field truncation, permission failures, sideband load/unload, BPF trampolines in kallsyms, and annotation lookup after unload.
