<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/errors.go -->
# sources/cloud-native/containers-storage/errors.go

## Purpose
`errors.go` re-exports canonical storage errors from `types` and defines one internal image-name operation error.

## Important APIs, Types, And Functions
Exported variables include container, image, layer, digest, duplicate, read-only, unsupported, load, mapping, and size errors such as `ErrContainerUnknown`, `ErrImageUnknown`, `ErrDuplicateName`, `ErrStoreIsReadOnly`, and `ErrInvalidMappings`. `errInvalidUpdateNameOperation` is package-internal.

## Control Flow
There is no dynamic control flow. Variables are aliases to `types` errors so callers can use the storage package API.

## State And Persistence
No state is stored beyond package-level error values.

## Dependencies And Integration Points
The file preserves public API compatibility while centralizing error definitions in `types`. Store, image, layer, container, and mapping code wrap these sentinels with contextual errors.

## Risks And Test Signals
Changing aliases would break `errors.Is` behavior and public compatibility. The internal update-name error is used by name mutation code.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/errors.go -->
