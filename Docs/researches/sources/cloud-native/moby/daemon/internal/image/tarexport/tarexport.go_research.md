## sources/cloud-native/moby/daemon/internal/image/tarexport/tarexport.go

Purpose: Defines shared tar export/load types and constructs the image exporter.

Important APIs/types: Constants `manifestFileName` and `legacyRepositoriesFileName`; `manifestItem` models Docker archive manifest entries with config path, repo tags, layer paths, optional parent, and optional foreign layer source descriptors. `tarexporter` holds image store, layer store, reference store, event logger, and optional platform matcher. `LogImageEvent` abstracts event logging. `NewTarExporter` returns an `image.Exporter`.

Control flow: Constructor stores dependencies and creates a strict platform matcher when a platform is supplied.

State and persistence: The struct is long-lived dependency state; load/save methods perform the actual persistence.

Dependencies and integration: Bridges the daemon image exporter interface to image/layer/ref stores and OCI/containerd platform matching.

Risks: All dependencies are interfaces or concrete stores expected to be non-nil; constructor does not validate them. Platform matching is strict, which can exclude images if metadata is incomplete.

Tests: No direct tests in this subset.
