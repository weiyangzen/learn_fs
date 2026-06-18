# Research: sources/cloud-native/nydus-snapshotter/pkg/filesystem/tarfs_adaptor.go

This adaptor exposes tarfs/blockdev operations through `Filesystem`. `TarfsEnabled` checks whether a `tarfs.Manager` is installed. `PrepareTarfsLayer` validates image ref, layer digest, and manifest digest labels, asks the tarfs manager whether the image has a tarfs hint annotation, optionally acquires a per-ref concurrency limiter, prepares the layer, releases the limiter, and annotates labels with the layer blob ID under `NydusTarfsLayer`.

Other methods are thin delegations: `MergeTarfsLayers`, `DetachTarfsLayer`, `ExportBlockData`, `GetTarfsImageDiskFilePath`, and `GetTarfsLayerDiskFilePath`. The filesystem mount path uses the `NydusTarfsLayer` label to switch to `FsDriverBlockdev` and call `MountTarErofs`.

State lives in tarfs manager storage and the mutable labels map. Integration points include containerd snapshot metadata, Nydus label constants, tarfs manager concurrency limiting, and block-data export. Risks include label mutation as control flow, misspelled error text, limiter release not deferred around all error paths, logging and continuing after `PrepareLayer` error before still labeling the layer, and no direct tests here.
