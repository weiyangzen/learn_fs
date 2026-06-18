<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/lookup/LookupIntentMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/lookup/LookupIntentMsgEx.cpp

## Purpose
Implements BeeGFS combined lookup intents: lookup, create, exclusive create, revalidate, stat, and open in one metadata message, with buddy-mirrored replay support and session insertion for opens.

## Important APIs, Types, and Functions
`lock()` chooses parent/name/file locks based on intent flags, pre-runs lookup for non-create intents under the parent lock, and handles directory/file lock ordering. `processIncoming()` validates parent/name and pre-generates a file ID for creates. `executeLocally()` sequences create, lookup, revalidate, stat, and open responses in one `LookupIntentResponseState`. Helpers include `lookup()` for dentry/inode data and remote metaVersion stat, `revalidate()`, `create()` through `MsgHelperMkFile`, `stat()` through `MsgHelperStat`, `open()` through `MsgHelperOpen` plus session store insertion, `getOpCounterType()`, and `forwardToSecondary()`.

## Control Flow, State, and Persistence
Create persists a new metadata file and optional remote storage target info, enforces quota if requested, fixes mirrored timestamps, logs file creation events, and forwards stripe pattern/new ID to the secondary. Open mutates file reference state and session stores, assigning a new owner FD on primary and replaying it on secondary. Stat may use inlined inode data from lookup or reload from disk. Revalidate compares client entry ID/owner and metaVersion.

## Dependencies and Integration Points
Depends on `MetaStore`, `DirInode`, `SessionStore`, `SessionTk`, `MsgHelperMkFile/Open/Stat/Trunc`, quota stores, storage pools, `StorageTk`, `StatMsg` for remote non-inlined revalidate, file-event logging, buddy group mapping, and `MirroredMessage`.

## Risks and Test Signals
Risks include complex lock ordering, create/lookup races, dangling dentries with null stripe patterns, remote stat failures during revalidate, secondary owner FD replay, quota checks across pool targets, and forwarding only when create/open changed observable state. Tests should cover every flag combination, exclusive create existing path, inlined versus non-inlined inode stat, remote-owner revalidate, open with trunc, mirrored primary/secondary create-open, and null stripe-pattern recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/lookup/LookupIntentMsgEx.cpp -->
