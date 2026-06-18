# sources/cloud-native/nydus/contrib/nydusify/pkg/checker/rule/bootstrap.go

## Purpose
This rule validates that a Nydus bootstrap is structurally valid and that blobs recorded inside the bootstrap are represented by manifest blob layers, except for OCI reference layers.

## Important APIs, Types, and Functions
`BootstrapRule` stores workdir, `nydus-image` path, parsed source/target images, and backend configs. `output` models `nydus-image check` debug JSON with a `blobs` array. Methods are `Name`, `validate`, and `Validate`.

## Control Flow
`validate` skips nil/non-Nydus parsed images, runs `nydus-image check` through `tool.Builder.Check` against the unpacked bootstrap path, reads and unmarshals debug output, builds a set of blob digests from all manifest layers except the final bootstrap and layers annotated as OCI reference layers, then ensures bootstrap blob IDs all appear in manifest layers when manifest blob layers are present. `Validate` applies this to source and target.

## State, Persistence, and Dependencies
It reads bootstrap files and writes/reads `nydus_output.json` under the checker workdir. Dependencies include checker tool builder, parser, nydus snapshotter label constants, utils bootstrap file name, JSON, and logrus.

## Integration Points
This rule depends on `checker.Output` having already unpacked bootstrap files. It integrates external `nydus-image` binary validation with manifest-level consistency checks.

## Risks and Test Signals
If there are no blob layers in the manifest, missing bootstrap blobs are tolerated. Blob digest comparison uses hex strings from descriptors. External binary failures are wrapped as invalid bootstrap format. Tests monkeypatch builder checks to cover success, missing blob mismatch, reference-layer skip, bad JSON, and missing output file.
