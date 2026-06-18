# sources/cloud-native/nydus/contrib/nydusify/pkg/checker/rule/manifest.go

## Purpose
This rule validates OCI and Nydus image manifest structure and compares source and target image configs when both are present.

## Important APIs, Types, and Functions
`ManifestRule` stores parsed source and target images. Methods include `Name`, `validateConfig`, `validateOCI`, `validateNydus`, `validate`, and `Validate`.

## Control Flow
`validate` skips nil parsed input, logs image type, then validates either OCI or Nydus image shape. OCI validation checks rootfs diff ID count equals layer count except for model artifacts. Nydus validation requires the final layer to be a bootstrap, non-final layers to be Nydus blob layers for non-model artifacts, model artifact annotation consistency on the final layer, and matching diff ID count. `Validate` runs source and target validation, then compares source and target `ImageConfig` JSON after normalizing deprecated `ArgsEscaped`.

## State, Persistence, and Dependencies
The rule is pure in-memory validation. Dependencies include JSON, reflection, model-spec artifact types, parser types, checker tool logging helpers, and utils annotation/media constants.

## Integration Points
It is the first rule run by checker and establishes basic manifest correctness before bootstrap and filesystem validation. It supports both normal container images and model artifacts.

## Risks and Test Signals
`validateNydus` indexes `layer.Annotations[...]` without checking nil maps, but reading from a nil map is safe in Go; however, empty layer lists would skip bootstrap validation and then only diff ID count may catch issues. Config comparison by marshaled JSON is strict and may flag semantically equivalent but differently normalized configs. Tests in `filesystem_test.go` cover name, OCI diff ID mismatch, Nydus bootstrap/blob validation, config equality/mismatch, and nil parsed input.
