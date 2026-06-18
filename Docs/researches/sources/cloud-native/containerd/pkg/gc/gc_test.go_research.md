<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/gc/gc_test.go -->
# sources/cloud-native/containerd/pkg/gc/gc_test.go

Purpose: tests and benchmark for GC reachability algorithms.

Important APIs and functions: `TestTricolorBasic`, `BenchmarkTricolor`, `TestConcurrentBasic`, `writeNodes`, `lookup`, `lookupc`, and `toNodes`.

Control flow and state: tests define a directed graph, mark reachable nodes from roots, then compare the retained/swept sequence with expected nodes. Concurrent tests feed roots through a channel and use callback-based reference expansion.

Dependencies and integration: standard testing, context, reflection, and local helper maps.

Risks and test signals: validates basic reachability and cycles but does not deeply stress cancellation or race behavior in `ConcurrentMark`. Benchmark creates a larger reference graph for allocation/performance signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/gc/gc_test.go -->
