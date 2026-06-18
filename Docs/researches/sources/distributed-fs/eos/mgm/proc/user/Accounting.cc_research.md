# sources/distributed-fs/eos/mgm/proc/user/Accounting.cc

## Purpose

`Accounting.cc` implements the legacy `ProcCommand::Accounting()` user command for EOS storage accounting. It exposes two subcommands: `config`, which lets sudoers tune the in-process accounting report cache, and `report`, which returns a JSON accounting document describing the storage service, capacity, and quota-backed storage shares.

## Important APIs, Types, and Functions

The main API is `int ProcCommand::Accounting()`. Internally it owns a static `eos::common::ExpiryCache<std::string>` with a default 600 second expiry and a static `generateAccountingJson(VirtualIdentity&)` lambda. The generator reads extended attributes through `gOFS->_attr_ls`, quota data through `Quota::GetAllGroupsLogicalQuotaValues()`, formats output with `Json::Value`, and returns a heap-allocated string for the cache to own. A nested `processAccountingAttribute` lambda recognizes keys prefixed with `sys.accounting`, splits dot-separated paths, creates nested JSON objects or array positions, and stores comma-separated values as JSON arrays.

## Control Flow

The command initializes `retc` to `SFS_OK`, then dispatches on `mSubCmd`. `config` first requires `pVid->sudoer`; it then parses `mgm.accounting.expired` and `mgm.accounting.invalid` as minute values, clamps them to minimums of 1 and 5 minutes, and updates the cache timing. `report` reads `mgm.option`, treats option `f` as force-refresh, and calls `accountingCache.getCachedObject(forceUpdate, generateAccountingJson, std::ref(*pVid))`. Unsupported subcommands return `ENOTSUP`.

## State and Persistence

Persistent source state comes from namespace xattrs under the MGM proc path and each quota path, especially `sys.accounting.*` metadata. Report state is cached in memory in a function-local static cache shared by all calls in the MGM process. Capacity and share usage are snapshots derived from quota state; no namespace state is mutated by `report`. `config` mutates only cache policy, not persisted metadata.

## Dependencies and Integration Points

The command integrates `ProcCommand` opaque request parsing, the global MGM object `gOFS`, quota aggregation, JSONCPP, `StringTokenizer`, and EOS version macros. It is part of the `/proc/user` command surface and depends on the same `stdOut`, `stdErr`, `retc`, `pOpaque`, and `pVid` fields as other legacy commands.

## Risks and Test Signals

The JSON path builder trusts `sys.accounting.*` attribute structure; malformed numeric path components can create arrays, and unexpected short keys could index the last component. Values containing commas are always converted to arrays, which may surprise callers expecting scalar strings. The generator allocates a new string for the cache callback, so cache ownership semantics matter. Test signals include sudo and non-sudo `config`, invalid numeric inputs, forced and cached `report`, xattr-driven nested JSON, quota paths with share metadata, and error propagation as `EAGAIN` on cache update failure.
