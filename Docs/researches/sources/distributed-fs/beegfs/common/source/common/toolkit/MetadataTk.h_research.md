<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/MetadataTk.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/MetadataTk.h

Purpose: Declares metadata lookup and file-type conversion helpers.

Important APIs/types: `ModificationEventType` enumerates metadata modification event kinds. `MetadataTk::referenceOwner` is the public owner-resolution API. Private helpers perform find-owner steps. Inline `posixFileTypeToDirEntryType` maps POSIX mode bits to BeeGFS entry types.

Control flow/state/persistence: Stateless API; owner lookup performs network communication in the implementation.

Dependencies/integration: Includes node stores, entry info, root info, path, storage errors, and messaging. Used by tools and services that need to locate metadata owners.

Risks/test signals: Tests should cover POSIX type mapping for regular, directory, symlink, and unknown modes, plus owner lookup integration with mirrored metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/MetadataTk.h -->
