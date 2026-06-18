# sources/distributed-fs/ceph-client/tools/perf/util/bpf-filter.l

Purpose: flex lexer for perf BPF sample-filter expressions. It tokenizes sample terms, operators, numeric literals, cgroup paths, and symbolic constants used by the parser.

Important APIs and tokens: lexer prefix is `perf_bpf_filter_`. It emits `BFT_SAMPLE`, `BFT_SAMPLE_PATH`, `BFT_OP`, `BFT_NUM`, `BFT_PATH`, `BFT_LOGICAL_OR`, and punctuation tokens. Helpers set `perf_bpf_filter_lval` with sample term/part, operation, numeric value, or path. Recognized sample terms include `ip`, `id`, `tid`, `pid`, `cpu`, `time`, `addr`, `period`, `txn`, `weight*`, page sizes, data-source subfields, `uid`, `gid`, and `cgroup`.

Control flow: numeric patterns parse decimal or hex. Sample keywords reset or set `perf_bpf_filter_needs_path`; only `cgroup` expects a following path token. Operators map to BPF filter ops. Many textual constants map to perf memory data-source bit values, such as load/store, cache levels, snoop states, remote, locked, TLB states, block reasons, and hop counts. Unexpected path-like text is an error unless the parser is waiting for a path.

State and persistence: lexer state is transient, but it mutates the global parser semantic value and the `perf_bpf_filter_needs_path` flag. No persistent storage is allocated here except returning `yytext` for paths during parse.

Dependencies and integration points: includes perf event ABI constants and parser header `bpf-filter-bison.h`. It feeds `bpf-filter.y` and ultimately `perf_bpf_filter__parse()`.

Risks: keyword order matters because `{path}` catches broad text. Constants must remain aligned with kernel/perf memory data-source encodings and BPF program interpretation. Path semantic values point to lexer text, so parser actions must consume them immediately.

Test signals: lexer/parser tests for every sample term, aliases, decimal/hex values, all comparison operators, `||`, comma separation, cgroup path acceptance, and unexpected token errors.
