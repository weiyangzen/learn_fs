<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/examples/lvs-eval/display.rs -->
# sources/control-plane/mayastor/io-engine/examples/lvs-eval/display.rs

Purpose: Pretty-printer for the `lvs-eval` example, exposing internal SPDK blobstore, bdev, and lvol allocation state.

Important APIs: `print_lvs()` prints base bdev, blobstore data, and replicas. `print_bdev()` displays name, size, block length, and block count. `print_lvs_data()` dereferences `spdk_blob_store` internals and prints metadata layout, free clusters, page usage, and bit arrays. `print_replicas()` iterates lvols; `print_replica()` prints lvol name/uuid/thin flag/cluster counts/size and active blob data. `print_blob_data()` dumps cluster IDs, LBAs, and extent pages. Private helpers print tables, bit arrays/pools, separators, and translate LBA to cluster.

State and dependencies: read-only introspection of live SPDK/LVS structures through unsafe pointers. Depends on `prettytable`, io-engine `Lvs/Lvol` traits, and raw libspdk structures.

Risks and test signals: tightly coupled to SPDK internal struct layout and unsafe pointer validity. It is diagnostic/example code, not production API. Test by running `lvs-eval` and checking output tables match expected allocations.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/examples/lvs-eval/display.rs -->
