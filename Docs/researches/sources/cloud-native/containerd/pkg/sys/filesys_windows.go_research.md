<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/sys/filesys_windows.go -->
# sources/cloud-native/containerd/pkg/sys/filesys_windows.go

## Purpose
Windows directory creation helpers that understand volume paths and optional LocalSystem/Administrators ACLs.

## Important APIs, Types, And Functions
SddlAdministratorsLocalSystem, MkdirAllWithACL, MkdirAll, mkdirall, mkdirWithACL, fixRootDirectory, and makeSecurityAttributes.

## Control Flow
MkdirAllWithACL builds security attributes from SDDL, then mkdirall recursively creates parents unless the path is a volume GUID path. mkdirWithACL uses CreateDirectory when ACL attributes are supplied.

## State And Persistence
Creates directories and security descriptors on disk. Volume GUID paths are treated as already existing roots.

## Dependencies And Integration Points
Depends on x/sys/windows, lazyregexp, syscall, unsafe. Used by Windows content/root/state setup code.

## Risks And Edge Cases
Code mirrors os.MkdirAll and must track compatibility. Incorrect root fixing for extended drive paths can break recursive creation. ACL applies inheritance to child objects.

## Test Signals
No local tests in subset; Windows integration paths cover it indirectly.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/sys/filesys_windows.go -->
