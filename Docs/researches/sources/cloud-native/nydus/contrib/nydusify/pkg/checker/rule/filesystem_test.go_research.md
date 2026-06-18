# sources/cloud-native/nydus/contrib/nydusify/pkg/checker/rule/filesystem_test.go

## Purpose
This test file covers pure filesystem rule helpers and also contains manifest/bootstrap rule name and manifest validation tests.

## Important APIs, Types, and Functions
Tests cover `FilesystemRule.Name`, `Node.String`, `ManifestRule.Name`, `BootstrapRule.Name`, `ManifestRule.validateOCI`, `ManifestRule.validateNydus`, `ManifestRule.validateConfig`, `ManifestRule.validate`, `FilesystemRule.walk`, `FilesystemRule.verify`, `getXattrs`, `mountImage`, and `Validate` skip behavior.

## Control Flow
Tests create temporary directory trees with files, subdirectories, and symlinks; walk them; compare identical and mismatched roots; and exercise manifest validation with synthetic OCI/Nydus images. No real mounts are performed except validation of the invalid-image branch.

## State, Persistence, and Dependencies
Temporary directories and files are created by tests. Dependencies include digest, OCI spec, parser, utils, and testify.

## Integration Points
The file is an important unit safety net for checker rule logic that can be tested without root privileges or external binaries.

## Risks and Test Signals
The tests do not exercise `mountOCIImage`, `mountNydusImage`, worker pool layer pulls, backend config generation, model artifact path, or unmount cleanup. Some manifest tests are located here rather than in `manifest_test.go`, which can make ownership less obvious.
