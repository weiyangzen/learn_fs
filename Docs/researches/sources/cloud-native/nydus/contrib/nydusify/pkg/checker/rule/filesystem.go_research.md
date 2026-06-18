# sources/cloud-native/nydus/contrib/nydusify/pkg/checker/rule/filesystem.go

## Purpose
This rule validates filesystem equivalence between source and target images by mounting them, walking both root filesystems, and comparing metadata, symlink targets, xattrs, and file content hashes.

## Important APIs, Types, and Functions
`FilesystemRule` stores workdir, `nydusd` path, source/target images, and backend configs. `Image` wraps parsed image and insecure flag. `Node` captures path, size, mode, rdev, symlink, UID, GID, xattrs, and hash. Key functions are `getXattrs`, `walk`, `mountNydusImage`, `mountOCIImage`, `mountImage`, `verify`, and `Validate`. `WorkerCount` controls source layer pull concurrency.

## Control Flow
`Validate` skips if either parsed image is nil, mounts source and target, defers unmounts, and calls `verify`. OCI mount pulls layers concurrently, unpacks them, and mounts overlay via `tool.Image`. Nydus mount builds `tool.NydusdConfig`, derives registry backend config if not supplied, enables digest validation for RAFS V5, handles model artifact external backend config, starts nydusd, and returns an unmount cleanup function. `verify` walks both trees concurrently and compares all nodes except root.

## State, Persistence, and Dependencies
Persistent/transient state includes layer unpack directories, mountpoints, nydusd cache/config/API socket directories, and external backend config files. Dependencies include parser, checker tools, utils, xattr library, model-spec, OCI reference parsing, syscall stat, worker pool, and logrus.

## Integration Points
This is the deepest end-to-end checker rule. It integrates registry pulls, tar unpacking, overlay mounting, nydusd mounting, backend configuration generation, and filesystem hashing.

## Risks and Test Signals
It requires privileges and working mount/nydusd binaries in real use. `walk` always hashes regular files, despite a comment suggesting backend-type gating, causing full data reads. Node comparison includes UID/GID/xattrs/rdev, which may vary by environment. `mountOCIImage` may leak readers because pulled layer readers are not explicitly closed in the visible code. Tests cover walking, node string, xattrs, verify success/missing/extra/mismatch, invalid mount image, and skip behavior, but not real mounts.
