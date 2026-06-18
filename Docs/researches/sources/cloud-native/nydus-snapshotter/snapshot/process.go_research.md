<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/snapshot/process.go -->
## sources/cloud-native/nydus-snapshotter/snapshot/process.go

Purpose: chooses how a `Prepare` operation should process a snapshot based on labels, fs driver, stargz/tarfs/index/referrer features, and whether the snapshot is a read-only layer or active writable layer.

Important API: `chooseProcessor`, returning a handler function, target snapshot reference, commit labels, and error. Handler variants include default native overlay preparation, skip/commit-only behavior, remote nydus mount preparation, and proxy mount preparation.

Control flow: for read-only layers (`containerd.io/snapshot.ref` present), proxy mode marks proxy labels and skips unpacking, nydus meta layers use native unpack, nydus data layers skip, index/referrer alternatives skip with labels, stargz data layers may generate metadata and skip, and tarfs may prepare/export tarfs then skip. For active layers, it checks proxy-parent mode, nydus meta parents, index/referrer alternatives, stargz merged metadata, and tarfs parent data; matching remote paths mount nydusd/tarfs and return overlay mounts. Unmatched paths fall back to native overlay/bind mounts.

Dependencies/integration: central integration point for config, labels, filesystem feature managers, containerd storage metadata, and tarfs/stargz conversion.

Risks and test signals: behavior is order-sensitive; a label or feature change can redirect snapshot lifecycle. Some error handling around parent snapshot info reads `pInfo` before checking `pErr` in the proxy-driver warning path. No direct tests here; `snapshot_test.go` covers only lower-level mount-native behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/snapshot/process.go -->
