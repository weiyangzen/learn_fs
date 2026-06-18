# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/btree_builder.rs

Builds persistent btrees from sorted key/value streams and optional shared prebuilt leaves. `RefCounter<Value>`, `NoopRC`, and `SMRefCounter` manage referenced values, while metadata blocks are allocated through `WriteBatcher`.

`NodeBuilder` buffers values, writes balanced leaves/internal nodes through `NodeIO`, imports underfull shared nodes when needed, increments metadata refs for reused nodes, and unshifts prior nodes to avoid underfull final nodes. `BTreeBuilder` builds leaves then calls `build_btree` to add internal layers. `release_leaves` drops temporary shared leaf references and decrements contained values when leaves become unreferenced.
