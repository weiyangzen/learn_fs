<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/cfg.h -->
# sources/distributed-fs/ceph-client/tools/bpf/bpftool/cfg.h

Purpose: this header exposes the bpftool eBPF control-flow graph dumping entry point.

Important APIs/types/functions: it includes `xlated_dumper.h` and declares `dump_xlated_cfg(struct dump_data *dd, void *buf, unsigned int len, bool opcodes, bool linum)`. The `dump_data` argument carries formatting and BTF/line-info context for instruction rendering.

Control flow: there is no executable control flow in the header. Its include guard prevents duplicate declarations.

State and persistence: no state is declared or persisted.

Dependencies and integration points: consumers call this from translated program dump code to produce DOT graphs. The declaration couples `cfg.c` to the xlated dumper's public data structure.

Risks: callers must pass a buffer containing whole `struct bpf_insn` records and a length in bytes. The header does not document ownership or validation; those assumptions are enforced only by implementation behavior.

Test signals: compile coverage is the main signal. Runtime graph tests belong to `cfg.c` and xlated dump command tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/cfg.h -->
