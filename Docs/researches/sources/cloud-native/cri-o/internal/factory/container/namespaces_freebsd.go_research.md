# sources/cloud-native/cri-o/internal/factory/container/namespaces_freebsd.go

## Purpose
Implements FreeBSD namespace handling by translating the sandbox network namespace path into a FreeBSD jail annotation.

## Important APIs, Types, And Functions
- `(*container).SpecAddNamespaces(sb SandboxIFace, targetCtr *oci.Container, serverConfig *config.Config) error` iterates sandbox managed namespaces and adds `org.freebsd.parentJail` for the network namespace.

## Control Flow
The method retrieves `sb.NamespacePaths()`, scans for `nsmgr.NETNS`, and writes the namespace path into the OCI spec annotations. Target PID containers and server config are unused on FreeBSD.

## State And Persistence
Mutates only the in-memory OCI spec annotations. The annotation names the parent jail used by downstream FreeBSD runtime handling.

## Dependencies And Integration Points
Integrates sandbox namespace metadata with the OCI spec generator through FreeBSD jail conventions. It depends on CRI-O namespace manager types and common `SandboxIFace`.

## Risks And Edge Cases
Only the network namespace is represented. Multiple network namespace entries would result in repeated annotation writes with the last value winning. Empty paths are not filtered here.

## Test Signals
No FreeBSD-specific test appears in this subset; behavior is compile-time platform-specific.
