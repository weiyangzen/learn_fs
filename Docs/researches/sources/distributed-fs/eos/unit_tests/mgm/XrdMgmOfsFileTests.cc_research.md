# sources/distributed-fs/eos/unit_tests/mgm/XrdMgmOfsFileTests.cc

## Purpose
Tests selected `XrdMgmOfsFile` helpers for open opaque parsing and client application-name selection. These helpers affect placement exclusions and policy/accounting labels for XRootD client operations.

## Important APIs, types, and functions
The tests cover `XrdMgmOfsFile::GetExcludedFsids()` and static `XrdMgmOfsFile::GetClientApplicationName(XrdOucEnv*, XrdSecEntity*)`. They use `XrdOucEnv`, `XrdSecEntity`, and entity attributes such as `xrd.appname`.

## Control flow
The excluded-fsid test creates open opaque data with `eos.excludefsid=2,4,6,8,10,144`, assigns it to a file object, and verifies all ids are parsed. The app-name test checks null inputs, no app tags, XRootD entity app tag fallback, and `eos.app` opaque override even without a client entity.

## State and persistence
State is per-file open opaque data and security entity attributes. No durable state is written, but parsed values influence runtime scheduling and traffic policy behavior.

## Dependencies and integration points
Depends on namespace file metadata, XRootD security/entity APIs, XrdOucEnv, MGM OFS file internals, and Google Test.

## Risks and test signals
Tests cover happy paths but not malformed fsid lists, duplicates, whitespace, nonnumeric entries, memory ownership of `openOpaque`, or precedence when both tags are empty/malformed. Exclusion parsing is placement-sensitive and should fail conservatively.
