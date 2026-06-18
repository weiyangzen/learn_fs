# sources/distributed-fs/ceph-client/tools/bpf/bpftool/netlink_dumper.c

`netlink_dumper.c` contains focused renderers for BPF-related netlink attributes discovered by `net.c`: XDP attachment data on links and classic TC BPF filter/action data. It exports `do_xdp_dump()` and `do_filter_dump()`.

The XDP path parses nested `IFLA_XDP` attributes, skips missing or `XDP_ATTACHED_NONE` state, and emits device name, ifindex, attachment mode, and program IDs. Multi-attachment mode produces generic/driver/offload entries in a JSON array or plain nested output; single mode emits one mode/id pair. This relies on `libbpf_nla_parse_nested()` and `libbpf_nla_getattr_*()` helpers.

The TC path handles classifier and action metadata. `do_filter_dump()` checks that `TCA_KIND` is `bpf`, starts a formatted object, emits device identity and kind, then calls `do_bpf_filter_dump()` for filter name, ID, and optional action list. Actions are parsed by priority through `TCA_ACT_*`; only action kind `bpf` is rendered, with action name and ID taken from `TCA_ACT_BPF_*` attributes.

There is no persistence; the file only translates netlink snapshots to stdout/JSON. Dependencies are Linux rtnetlink and tc BPF attribute definitions, libbpf netlink attribute helpers, shared `json_output`/`json_wtr`, and formatting macros from `netlink_dumper.h`. Risks include silent skips for unsupported non-BPF actions, parse failures returning libbpf netlink parse errors, plain formatting tightly coupled to macro punctuation, and assumptions that string attributes are present and NUL-terminated. Test signals should include XDP none/single/multi modes, TC BPF filters with and without actions, mixed non-BPF actions, malformed nested attributes, and JSON/plain parity under `bpftool net show`.
