# sources/distributed-fs/beegfs/client_module/source/common/toolkit/MetadataTk.h

## Purpose
Declares metadata helper types and inline initializers for create, open, and lookup-intent operations. It is the shared contract between VFS operations and BeeGFS metadata messages.

## Important APIs and types
Exports `CreateInfo`, `OpenInfo`, and `LookupIntentInfoIn`. `CreateInfo` carries entry name, uid/gid, mode, umask, preferred meta/storage target lists, exclusive-create flag, override storage pool, and optional `FileEvent`. `OpenInfo_init` converts Linux open flags into BeeGFS access flags through `OsTypeConv_openFlagsOsToFhgfs`. `LookupIntentInfoIn_init` records parent and name; `LookupIntentInfoIn_addEntryInfo`, `addMetaVersion`, `addOpenInfo`, and `addCreateInfo` layer optional revalidate/open/create inputs onto a lookup intent. `CreateInfo_setStoragePoolId` overrides the default invalid pool.

## State, dependencies, integration
The header integrates `EntryInfo`, `LookupIntentInfoOut`, `UInt16List`, Linux inode namespaces, and storage definitions. It holds borrowed pointers, so object lifetime is controlled by callers and outbound message construction.

## Risks and test signals
Several inline functions are non-`static` in the header, so include/link behavior depends on the build model. `LookupIntentInfoIn_init` does not initialize `metaVersion` or `isExclusiveCreate`; callers should only read those after adding the corresponding info. Tests should validate lookup-create-open combinations and flag conversion for paged versus non-paged opens.
