# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/veristat.cfg

## Purpose

This configuration file lists BPF object-name glob patterns that are interesting for tracking BPF verifier performance. The selected names are complex or historically expensive selftests such as flow dissectors, loop benchmarks, profilers, pyperf, strobemeta, redirect/load-balancer programs, sysctl/TCP header tests, USDT, verifier scale, XDP noinline, XDP synproxy, and search pruning.

## Important APIs, Types, and Functions

There is no executable API. The file is line-oriented input for tools such as `veristat` or wrapper scripts. Supported syntax is simple pattern text plus comments; the patterns include wildcards like `bpf_flow*`, `loop*`, `test_sysctl*`, `test_verif_scale*`, and `xdp_synproxy*`.

## Control Flow

Consumer tooling reads the file line by line, skips comments, and interprets each remaining line as an object/program selection pattern. The control flow is therefore external to this file.

## State and Persistence Behavior

No runtime state is owned here. The file persists a curated test selection under version control.

## Dependencies and Integration Points

It depends on BPF selftest object naming conventions and integrates with verifier-stat collection workflows that need a stable benchmark corpus. Renames in `tools/testing/selftests/bpf` must be reflected here to avoid silently dropping coverage.

## Risks and Test Signals

Risks are stale globs, overly broad matches that inflate CI runtime, and missing new expensive verifier cases. Signals are non-empty expansion of each glob against built selftest objects and stable `veristat` output for the configured corpus.
