## sources/distributed-fs/ceph-client/tools/lib/bpf/relo_core.h

Purpose: Declares the CO-RE relocation data structures and internal resolver/patcher APIs shared by libbpf and kernel builds.

Important APIs/types: `struct bpf_core_cand` and `struct bpf_core_cand_list` model target BTF type candidates. `struct bpf_core_accessor` and `struct bpf_core_spec` represent high-level and raw accessor paths, capped by `BPF_CORE_SPEC_MAX_LEN`. `struct bpf_core_relo_res` carries original/new relocation values, validation flags, poison decision, and memory-size adjustment metadata. Public declarations expose parse, format, calculate, patch, and type-compatibility helpers.

Control flow: The header has no runtime flow, but it defines the contract used by `relo_core.c`: parse a local spec, match candidates, compute a `bpf_core_relo_res`, then patch an instruction.

State/persistence: All state is transient and caller-owned. `bpf_core_spec` embeds fixed-size arrays, so callers avoid allocation but must honor the maximum depth.

Dependencies/integration: Includes `<linux/bpf.h>` for relocation kinds and BPF instruction types. It is consumed by libbpf object relocation code and by kernel-side BPF verifier support.

Risks: ABI/layout drift between this header and implementation can corrupt relocation behavior. `BPF_CORE_SPEC_MAX_LEN` rejects very deep access paths with `-E2BIG`. Callers must supply enough scratch `bpf_core_spec` storage for resolver internals.

Test signals: Build tests should include user and kernel include contexts. Relocation tests should validate all declared result flags, especially `poison`, `validate`, and memory-size fields.
