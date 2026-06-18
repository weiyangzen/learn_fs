# sources/distributed-fs/eos/mgm/tgc/AsyncUint64ShellCmd.hh

## Purpose
`AsyncUint64ShellCmd.hh` declares the asynchronous uint64 shell-command adapter used by tape-GC space statistics. It hides `std::future` management and exposes a poll-style API returning `AsyncResult<std::uint64_t>`.

## Important APIs, Types, And Functions
`AsyncUint64ShellCmd` has constructor `AsyncUint64ShellCmd(ITapeGcMgm&)`, alias `Uint64AsyncResult`, public `getUint64FromShellCmdStdOut(const std::string&)`, and private `runShellCmdAndParseStdOut(std::string)`. Members are `m_mutex`, `m_mgm`, `m_previousResult`, and `m_future`.

## Control Flow
The header-level contract says calls automatically launch a shell command if necessary and otherwise poll the current command. Only one command is active per instance, giving `SmartSpaceStats` stable previous-value semantics for one configured script path.

## State And Persistence
The class stores no durable data; it caches only the last successful integer and the in-flight future. Because the object owns a reference to `ITapeGcMgm`, it must not outlive the MGM adapter.

## Dependencies And Integration Points
It depends on `AsyncResult.hh`, `ITapeGcMgm.hh`, futures, mutexes, and strings. It is constructed inside `SmartSpaceStats`, which supplies the command string based on `SpaceConfig::freeBytesScript` and the space name.

## Risks And Edge Cases
The class is non-copyable by member composition but does not explicitly delete copy/move operations; future/mutex/reference members effectively prevent normal copying. Lifetime of the MGM reference is critical. The command interface is shell-string based, so production security depends on upstream script configuration and quoting.

## Test Signals
Compile tests should verify non-copy behavior. Runtime tests should use `DummyTapeGcMgm` to exercise value, pending, previous value, parse error, and concurrent caller serialization.
