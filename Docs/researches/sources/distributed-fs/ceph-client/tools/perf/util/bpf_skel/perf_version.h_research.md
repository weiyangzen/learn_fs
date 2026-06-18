# sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/perf_version.h

## sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/perf_version.h

Purpose: this header embeds the perf build version string into BPF `.rodata` metadata for tests and tooling.

Important API: `bpf_metadata_perf_version[] SEC(".rodata") = PERF_VERSION` is the only exported object.

Control flow and state: there is no runtime control flow. The build rule defines `PERF_VERSION`, and the value becomes part of the BPF object's read-only data.

Dependencies and integration: included by BPF metadata builds and verified by `tests/shell/record_bpf_metadata.sh`. It includes `vmlinux.h` and BPF helper definitions for section attributes.

Risks: builds that do not define `PERF_VERSION` will fail. Tests depend on section naming and symbol retention.

Test signals: run the BPF metadata shell test and inspect generated BPF object rodata for the version symbol.
