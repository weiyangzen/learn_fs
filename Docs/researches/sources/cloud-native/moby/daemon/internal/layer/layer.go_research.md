## sources/cloud-native/moby/daemon/internal/layer/layer.go

Purpose: Defines the layer store package contracts for read-only layers, writable layers, metadata, store operations, and common errors.

Important APIs/types: Errors include `ErrLayerDoesNotExist`, `ErrLayerNotRetained`, `ErrMountDoesNotExist`, `ErrMountNameConflict`, and `ErrMaxDepthExceeded`. `ChainID` and `DiffID` alias digest. Interfaces include `TarStreamer`, `Layer`, `RWLayer`, `Store`, and `DescribableStore`. `Metadata`, `MountInit`, and `CreateRWLayerOpts` describe lifecycle metadata and mount creation options. `ReleaseAndLog` releases a layer and logs cleanup metadata.

Control flow: Mostly declarations. `ReleaseAndLog` calls `Store.Release`, logs errors, and logs each removed layer metadata entry.

State and persistence: Interfaces abstract persistent graphdriver/layerdb state implemented elsewhere. `Metadata` reports removed layer state after release.

Dependencies and integration: This is the main boundary used by image store, tar export/import, distribution transfer, builder cache, and graphdriver integrations.

Risks: Interface contracts rely on callers balancing `Get/Register/CreateRWLayer` references with `Release/ReleaseRWLayer`. Misbalanced calls can leak layers or trigger retained-reference errors. `ReleaseAndLog` intentionally swallows release errors after logging.

Test signals: Many layer tests validate concrete implementations against these contracts.
