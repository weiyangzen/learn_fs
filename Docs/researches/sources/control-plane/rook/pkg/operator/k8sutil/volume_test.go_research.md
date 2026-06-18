# sources/control-plane/rook/pkg/operator/k8sutil/volume_test.go

## Purpose
This file validates path-to-volume-name sanitization and truncation.

## Important APIs, Types, and Functions
`TestPathToVolumeName()` enumerates path inputs and expected Kubernetes volume names.

## Control Flow, State, and Persistence
The test is pure and deterministic. The long-name case locks down the current hash suffix for a fixed input.

## Dependencies and Integration Points
It uses Go testing only. It protects volume naming for pod specs derived from paths.

## Risks
The test does not cover empty strings, paths made entirely of separators, names exactly at 63 characters, or possible collision behavior. Long-name expectation will change if `Hash()` changes.

## Test Signals
Signals include trimming leading/trailing hyphens, lowercase conversion, numeric preservation, broad symbol replacement, Unicode-to-hyphen handling, and long-name sample/hash formatting.
