# sources/cloud-native/moby/daemon/internal/system/filesys_windows.go

## Purpose
Provides Windows directory creation helpers that apply explicit ACLs while preserving `os.MkdirAll`-like behavior and volume-path handling.

## Important APIs, Types, And Functions
`SddlAdministratorsLocalSystem` grants full access to built-in Administrators and Local System with inheritance. `MkdirAllWithACL` converts SDDL to `windows.SecurityAttributes` and calls `mkdirAllWithACL`. `mkdirAllWithACL` mirrors Go's `os.MkdirAll` recursive logic. `mkdirWithACL` calls `windows.CreateDirectory`. `makeSecurityAttributes` builds inherited security attributes from SDDL.

## Control Flow
The helper first returns success for existing directories and `ENOTDIR` for existing non-directories. Otherwise it recursively creates parents until the volume root, then creates the target with the supplied security descriptor.

## State And Persistence
Creates directories on disk with the requested DACL. Security attributes are temporary process memory.

## Dependencies And Integration Points
Windows-only and likely used by daemon storage/runtime paths that need predictable permissions for service accounts.

## Risks And Test Signals
Behavior intentionally tracks Go 1.23.4 `MkdirAll`; upstream changes may need porting. Invalid SDDL or path conversion errors become `os.PathError`. No tests for this file are included in the subset.
