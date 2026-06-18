# sources/distributed-fs/ceph-client/tools/perf/util/bpf-filter.y

Purpose: bison grammar for BPF sample-filter expressions. It builds `perf_bpf_filter_expr` lists consumed by `bpf-filter.c`.

Important APIs and grammar: the parse parameter is `struct list_head *expr_head`. `filter` accepts comma-separated terms. `filter_term` supports `filter_expr || filter_expr` by creating a `PBF_OP_GROUP_BEGIN` expression and adding member expressions to its `groups` list. `filter_expr` accepts numeric comparisons for sample terms and path comparisons for cgroup terms. Cgroup comparisons are limited to `==` and `!=`.

Control flow: each parsed top-level expression is appended to `expr_head`. OR groups are flattened one level by storing a group begin node whose `val` counts members, then later `bpf-filter.c` emits member entries followed by `PBF_OP_GROUP_END`. For cgroup paths, the parser creates a cgroup object, reads its cgroup id, and stores that id as the comparison value.

State and persistence: expression nodes are heap allocated through `perf_bpf_filter_expr__new()` and owned by the evsel filter list after parsing. The parser uses the global `perf_bpf_filter_needs_path` flag coordinated with the lexer.

Dependencies and integration points: includes Linux list helpers, cgroup utilities, and `bpf-filter.h`. It is invoked by `perf_bpf_filter__parse()`.

Risks: nested OR groups are not supported. If cgroup lookup fails, the expression value remains zero, which could match an unintended id unless callers treat zero carefully. Error reporting uses `printf` rather than perf's usual `pr_err`.

Test signals: parser tests for comma lists, OR groups of more than two expressions, numeric comparisons, cgroup equality/inequality, invalid cgroup operators, bad paths, and parser cleanup on syntax errors.
