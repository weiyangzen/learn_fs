# sources/cloud-native/containerd/internal/fsview/mount.go

## Purpose
Builds read-only `fs.FS` views from containerd mount descriptions without performing kernel mounts when possible.

## Important APIs, Types, And Functions
`View` extends `fs.FS` with `Close`. `FSMounts` resolves the last mount. `resolveMount` handles registered handlers, bind/rbind, overlay, and `format/.../overlay`. Helpers open bind paths, overlay paths, format templates, and template suffixes.

## Control Flow
Mount resolution tries registered handlers first, then built-ins. Bind opens an `os.Root`. Overlay collects upper/lower paths and creates an overlay view. Format overlays evaluate templates with `source`, `mount`, and `overlay` functions that can resolve preceding mounts and optional suffixes.

## State And Persistence
Views own open root/file resources and close them through composed cleanup functions. No persistent filesystem changes are made.

## Dependencies And Integration Points
Depends on `core/mount`, `errdefs`, `os.OpenRoot`, `io/fs`, and text templates. Plugins extend behavior through `Register`.

## Risks
Template execution can open multiple resources and must close on errors. Only known mount types are supported. Overlay path option parsing is simple and may not cover all kernel overlay options.

## Test Signals
`mount_test.go` and `mount_format_test.go` cover bind-last behavior, EROFS plugin views, overlay format templates, suffix handling, and unsupported mount errors.
