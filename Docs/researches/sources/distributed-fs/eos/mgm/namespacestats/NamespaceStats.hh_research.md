# sources/distributed-fs/eos/mgm/namespacestats/NamespaceStats.hh

## Purpose
`NamespaceStats.hh` declares the MGM implementation of the namespace statistics interface. It lets namespace services report counters and execution timings without depending directly on MGM's `Stat` class.

## Important APIs, Types, And Functions
`NamespaceStats` derives from `INamespaceStats`. It exposes a default constructor, `Add(const char* tag, uid_t uid, gid_t gid, unsigned long val)`, and `AddExec(const char* tag, float exectime)`, both marked `override`.

## Control Flow
The header contains no executable flow. The interface methods are called by namespace code and implemented in the `.cc` as forwarding methods into MGM stats.

## State And Persistence Behavior
The class declares no members. It is a stateless adapter; all durable or aggregate stat behavior belongs to the target MGM statistics object.

## Dependencies And Integration Points
It includes `mgm/Namespace.hh` for MGM namespace macros and `namespace/interface/INamespaceStats.hh` for the base interface. `XrdMgmOfs.hh` includes this header and embeds `eos::mgm::NamespaceStats mNamespaceStats`.

## Risks And Edge Cases
Because the class is stateless and relies on global MGM state in its implementation, tests and alternate namespace hosts need a valid MGM singleton or a different `INamespaceStats` implementation. Any signature drift in `INamespaceStats` will break this override at compile time.

## Test Signals
Compile coverage should confirm interface conformance. Integration tests should construct the namespace group with MGM stats wired in and assert counters/timings appear in `MgmStats` under the expected tags.
