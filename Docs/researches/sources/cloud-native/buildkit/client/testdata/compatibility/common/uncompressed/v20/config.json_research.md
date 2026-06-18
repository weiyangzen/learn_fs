# sources/cloud-native/buildkit/client/testdata/compatibility/common/uncompressed/v20/config.json

## Purpose
This JSON fixture is an image configuration document for the BuildKit client compatibility suite. It belongs to the `common/uncompressed/v20` fixture, which represents the common fixture shared by exporter compatibility tests across image layout modes and the uncompressed layer media type baseline.

## Important Fields and Data Shape
- Platform: `linux/amd64` with created timestamp `2015-10-21T07:28:00Z`.
- Runtime config: env count `1`, command `['sh']`, working directory ``, entrypoint `None`, labels `None`.
- Root filesystem: type `layers`, diff ID count `4`, first diff ID `sha256:fe4922f0a3ca2aa70...`.
- History: `5` entries, including BuildKit exporter history comments for generated layers.
- Compatibility version directory: `v20`.

## Control Flow and Integration Role
The file is loaded as fixture data rather than executed. Compatibility tests compare generated exporter config JSON against this baseline to detect changes in platform fields, rootfs diff IDs, history ordering, Docker legacy fields, command/env defaults, and BuildKit-created history records.

## State and Persistence Behavior
The document is immutable testdata. It models persisted image configuration that would be stored as a content-addressed config blob and referenced by a manifest. Any byte-level change can alter the config digest and therefore the expected manifest descriptor.

## Dependencies and Integration Points
It integrates with image/OCI exporter compatibility tests under `client/testdata/compatibility`, the container image exporter metadata path, and manifest fixtures in adjacent directories. The config's diff IDs must align with layer descriptors in the corresponding manifest fixture.

## Risks and Edge Cases
The main risk is accidental fixture drift: changing timestamps, history text, Docker legacy fields, or diff ID ordering can break reproducibility and compatibility assertions. Variant-specific compression changes should not alter uncompressed diff IDs unless the actual filesystem content changes.

## Test Signals
A matching config indicates the exporter preserved expected image config schema, platform, rootfs, and history semantics for `uncompressed` under compatibility version `v20`. A mismatch usually signals exporter output drift rather than runtime code execution in this file.
