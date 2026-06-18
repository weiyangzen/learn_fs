# Research: sources/cloud-native/nydus-snapshotter/pkg/label/label.go

This file centralizes label keys used to coordinate containerd snapshot metadata, Nydus image metadata, proxy mode, tarfs, stargz, signatures, and index alternatives. It aliases containerd snapshotter label names for compatibility and preserves the old exported `AppendLabelsHandlerWrapper` name.

Important constants include `TargetSnapshotRef`, `NydusDataLayer`, `NydusMetaLayer`, `NydusRefLayer`, `NydusTarfsLayer`, block verity labels, pull secret/user labels, `NydusProxyMode`, `NydusSignature`, `StargzLayer`, `OverlayfsVolatileOpt`, `TarfsHint`, and `NydusIndexAlternative`. Helper functions check map-key presence for Nydus data/meta layers, tarfs data layers, proxy mode, and tarfs hints.

There is no persistence here, but labels are persisted in containerd snapshot/image metadata and are used throughout filesystem preparation, metadata detection, tarfs/stargz adaptors, and proxy mode. Risks include key-presence checks treating empty values as true, mutable label maps being used as state transfer, and semantic drift between containerd labels and project constants. There are no direct tests in this subset; behavior is indirectly exercised by higher-level mount and detector tests.
