<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperMkFile.h -->
# sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperMkFile.h

## Purpose
Declares the static metadata file creation helper.

## Important APIs, Types, and Functions
`MsgHelperMkFile::mkFile()` is the sole public method and takes parent directory, create details, target/pattern parameters, optional `RemoteStorageTarget`, output entry/inode data, and optional storage pool ID. Construction is disabled by a private constructor.

## Control Flow, State, and Persistence
The header establishes ownership-sensitive parameters: callers may pass a raw `StripePattern*` that the implementation assumes ownership of on success path.

## Dependencies and Integration Points
Includes storage errors, `MetaStore`, and `MkFileDetails`; forward-declares the create details struct. Used by file-create message handlers.

## Risks and Test Signals
Tests and call sites should verify raw pointer ownership expectations and that optional output pointers can be null only where `MetaStore::mkNewMetaFile()` supports it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperMkFile.h -->
