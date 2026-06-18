# sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/FileMDSvc.cc

## Purpose
This file implements `QuarkFileMDSvc`, the QuarkDB-backed EOS file metadata service. It manages file metadata retrieval, creation, update, deletion, cache integration, listener notification, and shared setup of the metadata provider and unified inode provider.

## Important APIs, Types, and Functions
`configure()` parses QDB contact details when `qdb_flusher_md` is present, configures the meta hash and inode provider, creates `MetadataProvider`, and injects it plus the inode provider into `QuarkContainerMDSvc`. It can refresh inode state and set file cache size. `initialize()` checks the container service and qclient/flusher, runs `SafetyCheck()`, and initializes `mNumFiles`.

`SafetyCheck()` probes sparse ids above `getFirstFreeId()` using `MetadataFetcher::getFileFromId()`. `getFileMDFut()` and `getFileMD()` retrieve through `MetadataProvider`. `hasFileMD()` checks existence. `createFile()` reserves or blacklists ids, constructs `QuarkFileMD`, inserts it into cache, emits a Created event, and increments count. `updateStore()` writes the file protobuf and adds detached files (`cont_id == 0`) to the orphan set. `removeFile()` deletes the protobuf, removes the orphan-set entry, emits a Deleted event, tombstones the object, and decrements count. `setContMDService()` enforces the concrete Quark container service type.

## Control Flow
The file service is the owner of `MetadataProvider`; provider construction creates its own qclients and shards. During configuration it wires the provider and inode provider into the container service. Normal reads return futures or block on them. Creates notify listeners before persistence, while updates and deletes enqueue writes through the flusher. The destructor synchronizes the flusher if present.

## State and Persistence Behavior
Persistent state includes file protobufs, namespace metainfo, max inode values, and the orphan file set. In-memory state includes listener list, quota pointer, container service pointer, flusher/qclient pointers, metainfo hash, atomic count, metadata provider, and unified inode provider. Newly created or fetched metadata objects are cached in `MetadataProvider`; removed objects are marked deleted to act as cache tombstones.

## Dependencies and Integration Points
It depends on QuarkDB configuration parsing, constants, `QuarkFileMD`, `QdbContactDetails`, quota stats, metadata flusher, container service, metadata fetcher/provider, request builder, and string conversion. It implements `IFileMDSvc` for the namespace stack and coordinates with `QuarkContainerMDSvc`.

## Risks and Test Signals
`configure()` assumes `pContSvc` is already set and that it is a `QuarkContainerMDSvc`; misordered configuration can crash or throw. File cache size updates assume `mMetadataProvider` already exists. Empty-name updates log and return, risking silent lost writes. Creates notify listeners before durable write. Tests should cover configuration ordering, explicit-id blacklist, first-free id refresh, missing dependency errors, orphan-set updates, listener events, tombstone behavior, cache stats, and safety-check failures.
