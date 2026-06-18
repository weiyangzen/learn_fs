# sources/distributed-fs/eos/mgm/ofs/XrdMgmOfsDirectory.hh

## Purpose
`XrdMgmOfsDirectory.hh` declares the EOS MGM directory object used by XRootD OFS. It defines the directory-open, iteration, close, and error-reporting interface plus the state used to cache a resolved namespace listing.

## Important APIs and types
- `class XrdMgmOfsDirectory : public XrdSfsDirectory, public eos::common::LogId` is the concrete SFS directory implementation.
- `open(const char* dirName, const XrdSecClientName* client = 0, const char* opaque = 0)` declares the client-authenticated entry point. The implementation uses the corresponding XRootD security entity type.
- `open(const char* dirName, eos::common::VirtualIdentity& vid, const char* opaque = 0)` supports internal callers with a precomputed EOS identity.
- `_open(...)` is the low-level implementation after mapping, bounce, access mode, stall, and redirect decisions.
- `nextEntry()` returns a null-terminated name pointer or null at EOF/error.
- `Emsg(...)` writes error text and code into an `XrdOucErrInfo`.
- `close()` releases listing state.
- `FName()` exposes the currently opened directory path.
- `listing_t` is `std::set<std::string>`, giving sorted, unique entries.
- `dirCache` is a static `eos::common::LRU::Cache<std::string, std::shared_ptr<listing_t>, std::mutex>`.

## Control flow and state shape
The header shows a two-layer open model: public overloads receive either XRootD auth data or a `VirtualIdentity`; both normalize and authorize before `_open` fills `dh_list` and `dh_it`. Iteration is stateful: `nextEntry()` advances `dh_it`, while `close()` clears `dh_list`. `getCacheName` is private and exists to couple cache keys to namespace metadata timestamps and listing filters.

The instance state is intentionally small: `dirName` for diagnostics, `vid` for the mapped caller, `dh_list`/`dh_it` for the materialized result, and `mDirLsMutex` to serialize access to that result. The cache is shared across all directory objects.

## Dependencies and integration points
The declaration pulls in EOS logging, mapping, LRU cache support, XRootD error/security/SFS interfaces, POSIX `dirent`, and STL containers/mutexes. It forward-declares `eos::IContainerMD`, matching the implementation's namespace metadata dependency while keeping the header relatively light.

## Risks and edge cases
- The declaration names `XrdSecClientName` while the implementation uses `XrdSecEntity`; this may depend on typedef compatibility or may be a stale declaration risk worth checking against the active XRootD headers.
- Returning raw `const char*` from `nextEntry()` exposes lifetime coupling to `dh_list`.
- `listing_t` as `std::set` sorts entries and removes duplicates, which may differ from physical namespace order but gives deterministic XRootD responses.
- Static cache state has process-wide memory and coherency implications.

## Test signals
Header-level regression signals include compile coverage against the active XRootD SFS signature, construction/destruction through `XrdSfsDirectory` pointers, concurrent `nextEntry`/`close` access, cache type instantiation, and ABI compatibility for plugin loading.
