# sources/distributed-fs/eos/mgm/access/Access.hh

Purpose: declares the static `eos::mgm::Access` rule engine used for global bans, allows, stalling, redirection, rate limits, and thread limits. It is a process-wide configuration facade rather than an instantiable request object.

Important APIs and types: string constants define global config keys such as `BanUsers`, `AllowedHosts`, `Stall`, `Redirection`, `StallHosts`, and `NoStallHosts`. Static sets/maps hold banned/allowed identities, stall/redirection rules, comments, and per-user/group redirection placeholders. `StallInfo` carries a stall type, delay, comment, and global flag. Public static methods load/store/reset config and query limits.

Control flow: callers update the static containers, then call `StoreAccessConfig`, or refresh from persistent config with `EnforceConfig`. Request paths query booleans/maps and may call `CanStall` or limit helpers under `gAccessMutex`.

State and persistence: all rule state is static and guarded by `eos::common::RWMutex gAccessMutex`; the implementation persists it via `FsView::gFsView`.

Dependencies and integration points: includes namespace macros, EOS `RWMutex`, `Mapping`, STL sets/maps/vectors/strings, and atomics. Documentation notes use by `XrdMgmOfs::ShouldStall` and `ShouldRedirect`.

Risks: public static containers make it easy to bypass helper invariants and forget lock discipline. Atomic summary flags can drift from maps if callers mutate maps directly. Several comments have copy/paste inaccuracies, which can mislead maintainers about host/domain/token semantics.

Test signals: header-level compile tests should include this from multiple MGM units; behavioral tests should mutate through helpers rather than raw containers and verify lock-protected readers observe consistent state.
