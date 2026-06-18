# sources/cloud-native/moby/daemon/volume/mounts/linux_parser.go

## Purpose
Linux mount parser and validator for raw `-v`-style specs and structured API `mount.Mount` configs.

## Important APIs, Types, And Functions
`NewLinuxParser` creates `linuxParser`. Important functions include `ValidateMountConfig`, `validateMountConfigImpl`, `ParseMountRaw`, `ParseMountSpec`, `ParseVolumesFrom`, `ConvertTmpfsOptions`, `ReadWrite`, `DefaultPropagationMode`, `DefaultCopyMode`, `IsBackwardCompatible`, and `ValidateTmpfsMountDestination`.

## Control Flow
Validation enforces exclusive option structs, non-empty absolute non-root targets, bind source presence/absolute path/existence unless raw parsing skips existence, volume subpath locality, tmpfs source absence and option validity, and image source/subpath rules. Raw parsing splits on up to three colon fields, distinguishes bind from volume by absolute source path, applies read-only, driver, copy, and propagation modes, then delegates to structured parsing. Structured parsing normalizes targets/sources, initializes `MountPoint`, and fills volume name/driver/copy, bind propagation, tmpfs, or image source fields. Tmpfs conversion serializes read-only, mode, size suffix, and a small option allowlist.

## State And Persistence
Parser has no persistence. It may query filesystem existence through `fileInfoProvider`.

## Dependencies And Integration Points
Used by daemon container create/update validation, volume service name validation, and mount setup. Depends on API mount types, shared copy mode helpers, and `MountPoint`.

## Risks
Colon grammar, path normalization, and raw-vs-structured bind source existence differences are compatibility-sensitive. Subpath validation is lexical; runtime symlink safety is handled later by `safepath`. Tmpfs option allowlist is intentionally narrow.

## Test Signals
Linux parser tests cover raw syntax, invalid modes, propagation, bind/volume parsing, file-info errors, structured validation, tmpfs option conversion, and fuzz crash resistance.
