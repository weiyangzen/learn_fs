<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_exporter.go -->
# sources/cloud-native/moby/daemon/images/image_exporter.go

Purpose: delegates save/load image archive behavior to the legacy tar exporter.

Important APIs and control flow: `ExportImage` and `LoadImage` accept zero or one platform only, reject multiple platforms with invalid-parameter errors, create a `tarexport.TarExporter` over the image, layer, reference stores and service, then call `Save` or `Load`.

State and persistence: `ExportImage` reads image/layer/ref state and writes to the caller stream. `LoadImage` reads a tar stream and can create image, layer, and reference records.

Dependencies and integration: backs API `docker save`/`docker load` for the legacy store and explicitly points multi-platform users to a containerd-snapshotter store.

Risks: multi-platform archives are not supported by this backend. Stream errors and partial loads are delegated to `tarexport`, so callers rely on its cleanup guarantees.

Test signals: no direct tests in this subset; save/load integration tests are the primary coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_exporter.go -->
