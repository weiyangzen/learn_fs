# sources/distributed-fs/eos/mgm/tgc/AsyncUint64ShellCmd.cc

## Purpose
`AsyncUint64ShellCmd.cc` implements a one-command-at-a-time asynchronous shell-command poller. It starts a command through the `ITapeGcMgm` abstraction, parses stdout as `uint64_t`, and returns an `AsyncResult` describing readiness, cached previous output, or error.

## Important APIs, Types, And Functions
The implementation defines the constructor, `getUint64FromShellCmdStdOut()`, and `runShellCmdAndParseStdOut()`. It uses `std::async(std::launch::async)`, `std::future::wait_for(0s)`, `ITapeGcMgm::getStdoutFromShellCmd()`, and `CtaUtils::toUint64()`.

## Control Flow
`getUint64FromShellCmdStdOut()` locks `m_mutex`, starts a new async task when no future is valid, polls immediately, and returns one of: `VALUE` when the future is ready and parsed successfully, pending with prior result if a previous command succeeded, or pending without prior result. On any exception it clears the previous result and returns `ERROR`.

## State And Persistence
State is process-local: a mutex, MGM reference, optional previous result, and the current future. A successful ready result invalidates the future and makes the parsed value the previous result for later pending calls. Errors reset the previous result.

## Dependencies And Integration Points
The class is used by `SmartSpaceStats` for optional free-byte scripts. It delegates shell execution to `ITapeGcMgm`, so production uses `RealTapeGcMgm::getStdoutFromShellCmd()` and unit tests can use `DummyTapeGcMgm`.

## Risks And Edge Cases
The mutex is held while calling `future.get()`, so if task completion triggers expensive exception construction or cleanup, polling is serialized. The `cmdStr` parameter is only used to start a new command when no command is in flight; callers changing the command while a previous command runs still observe the older task. A parsing or shell error clears the previous result, causing subsequent pending states to fall back to internal stats.

## Test Signals
Tests should cover first pending, ready value, previous-value pending, parse failure, shell timeout/error propagation through the MGM interface, repeated calls while in flight, and command changes while an older future is still valid.
