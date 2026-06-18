# sources/cloud-native/containers-storage/drivers/overlay/check.go

## Purpose
`overlay/check.go` implements active Linux overlayfs feature probes for native diff safety, metacopy, volatile mounts, idmapped lower layers, and data-only layers.

## Important APIs, Types, And Functions
Functions include `doesSupportNativeDiff`, `doesMetacopy`, `doesVolatile`, `supportsIdmappedLowerLayers`, and `supportsDataOnlyLayers`.

## Control Flow
Each probe creates temporary lower/upper/work/merged directories under the driver home, performs an overlay mount with relevant options, mutates or inspects files, reads overlay xattrs, then unmounts and removes the temporary tree. Native diff detection checks opaque xattr copy-up and redirect-dir behavior. Metacopy detection chmods a lower file and checks for the metacopy xattr. Idmapped support creates a user namespace process and an ID-mapped lower mount before overlay mounting it.

## State And Persistence
Temporary directories and kernel mounts are created and cleaned up. Results are returned to caller; caching is handled elsewhere in overlay driver code.

## Dependencies And Integration Points
The probes feed overlay driver initialization and capability decisions. Dependencies include `archive` overlay xattr helpers, `idmap`, `idtools`, `ioutils`, `mount.ParseOptions`, `system`, `unshare`, `unix`, and logrus.

## Risks
Probes require mount privileges and kernel support; failures may mean unsupported feature or hard error depending on context. Cleanup runs in defers and logs unmount/remove failures. Native diff safety is sensitive to overlay kernel behavior around opaque and redirect xattrs.

## Test Signals
Overlay driver tests indirectly cover cached use of these probes. Direct unit tests are difficult because behavior is kernel-dependent.
