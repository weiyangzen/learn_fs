# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/options/MountInfo.java

## Purpose
`MountInfo` is the immutable holder for one Alluxio mount point: the Alluxio URI, UFS URI, mount id, and `MountPOptions`. It converts internal mount metadata into gRPC and wire objects used by clients and web UI.

## Important APIs, types, and functions
The constructor validates non-null Alluxio and UFS URIs. Accessors expose `getAlluxioUri()`, `getUfsUri()`, `getOptions()`, and `getMountId()`. `toUfsInfo()` builds a gRPC `UfsInfo`. `toMountPointInfo()` builds a wire `MountPointInfo` with URI, read-only/shared flags, properties, and mount id. `toDisplayMountPointInfo()` converts properties through `UnderFileSystemConfiguration` with display-value masking. Equality compares mount id, URIs, read-only flag, and shared flag; `hashCode` includes full options.

## Control flow
The methods are direct transformations. Display conversion creates a mount-specific UFS configuration and asks it for a user property map using display-value options so sensitive or formatted values are suitable for display.

## State and persistence behavior
The object holds constructor-provided mount state in final fields and does not journal itself. Mount-table code persists and reconstructs mount metadata elsewhere. The `MountPOptions` object is retained by reference.

## Dependencies and integration points
It integrates with `MountTable`, gRPC mount APIs, `UfsInfo`, wire `MountPointInfo`, and UFS configuration display masking. REST and web UI mount-table endpoints consume the converted wire form.

## Risks
`equals` ignores mount properties except read-only/shared, while `hashCode` includes `mOptions`, which can violate the Java equality/hashCode contract if options differ only in properties. Retaining `MountPOptions` by reference assumes protobuf immutability. Display masking depends on UFS configuration property metadata.

## Test signals
Tests should check conversion fields, display masking for sensitive properties, equality/hash behavior with differing property maps, read-only/shared comparisons, and mount id propagation.
