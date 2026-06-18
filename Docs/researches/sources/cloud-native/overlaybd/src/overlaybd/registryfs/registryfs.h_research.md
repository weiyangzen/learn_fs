# sources/cloud-native/overlaybd/src/overlaybd/registryfs/registryfs.h

## Purpose
Declares the public registry filesystem and uploader interfaces used to read from and push to OCI-compatible registries.

## Important APIs and Types
`RegistryFS` extends `photon::fs::IFileSystem` with `setAccelerateAddress`. `PasswordCB` supplies username/password pairs. C exports create v1 and v2 registry filesystems, create a registry uploader wrapping a local file, and finalize an upload while returning its digest.

## Control Flow
Consumers choose `new_registryfs_v1` or `new_registryfs_v2`, open registry blob URLs as files, optionally set an acceleration proxy prefix, and read through Photon file APIs. Upload consumers create an uploader, stream data via `write`, then call `registry_uploader_fini` to fsync/finalize and retrieve the sha256 digest.

## State and Persistence
The header defines no state itself. Implementations maintain auth, URL, HTTP-client, and upload state, while upload data is staged in the caller-supplied local file.

## Dependencies and Integration Points
Depends on Photon callbacks and filesystem abstractions. The C ABI makes the functions usable from plugin-style or dynamically linked integration code.

## Risks
Defaults use `uint64_t timeout = -1`, relying on implementation timeout semantics. The v1 factory reserves an unused sixth argument while v2 treats it as customized user agent, so callers must use the correct version.

## Test Signals
Compile/link checks for the C exports, read-only file behavior through `IFileSystem`, acceleration address behavior, and uploader finalize digest checks are the expected signals.
