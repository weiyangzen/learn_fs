# sources/distributed-fs/eos/namespace/ns_quarkdb/tests/EosNamespaceBenchmark.cc

Purpose: Nominal namespace performance benchmark source, but the real benchmark implementation is disabled with `#if 0`.
Important APIs/types/functions: disabled code defines `bootNamespace`, `closeNamespace`, `PrintStatus`, `RThread`, `RunReader`, and a CLI-style main that creates directory/file trees and measures parallel reads with/without a global `RWMutex`; active code is only `int main(){ return 0; }`.
Control flow: active executable exits immediately. Disabled flow would create namespace services manually, populate `/eos/nsbench/...`, collect Linux stat/memory metrics, and spawn XRootD threads for read benchmarks.
State/persistence: active path has none; disabled path would persist large metadata sets in QDB.
Dependencies/integration: includes EOS namespace services, timing/memory helpers, XRootD thread/string types, and POSIX headers.
Risks: benchmark binary currently gives a false sense of coverage/performance measurement because all work is compiled out; disabled code may be stale relative to `QuarkNamespaceGroup` fixture patterns.
Test signals: no active behavioral signal beyond successful compilation/linking.
