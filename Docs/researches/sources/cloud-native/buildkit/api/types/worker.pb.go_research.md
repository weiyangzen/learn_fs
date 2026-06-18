# sources/cloud-native/buildkit/api/types/worker.pb.go

Purpose: generated Go bindings for `api/types/worker.proto`, carrying BuildKit worker inventory data over protobuf APIs. It defines `WorkerRecord`, `GCPolicy`, `BuildkitVersion`, and `CDIDevice` plus descriptor metadata for reflection.

Important APIs/types/functions: `WorkerRecord` exposes worker ID, labels, supported OCI platforms, GC policies, BuildKit version, and CDI devices. `GCPolicy` carries all/keep-duration/filter and reserved/max/min space fields. `BuildkitVersion` exposes package/version/revision/dockerfile version. `CDIDevice` exposes device name, auto-allow, annotations, and on-demand. Generated methods include `Reset`, `String`, `ProtoReflect`, deprecated `Descriptor`, getters, and package-level `File_github_com_moby_buildkit_api_types_worker_proto`.

Control flow: there is no business logic; protobuf runtime calls `file_github_com_moby_buildkit_api_types_worker_proto_init` during init to build message descriptors, map-entry metadata, exporter hooks, and dependency indexes. Getter methods return zero values when receivers are nil.

State and persistence behavior: message fields are in-memory protobuf state and unknown fields. Persistence is through protobuf binary/JSON serialization controlled by the generated descriptors. Field numbers preserve compatibility; `reservedSpace` intentionally keeps field number 3 after being renamed from `freeBytes`.

Dependencies and integration points: imports BuildKit solver `pb.Platform` and `google.golang.org/protobuf` reflection/runtime packages. This file is consumed by APIs that expose worker capabilities, GC policy, versioning, and CDI device metadata.

Risks: hand editing would be overwritten and can break descriptor invariants. Field-name casing (`ID`, `GCPolicy`, `CDIDevices`) is schema-driven and affects JSON/protobuf compatibility. Compatibility depends on preserving numeric tags, especially the renamed GC space field.

Test signals: no direct tests here; coverage comes from API round trips and users of the generated types. The paired vtproto file adds faster clone/equality/marshal paths for the same messages.
