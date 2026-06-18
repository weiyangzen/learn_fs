<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/extra.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/extra.go

## Purpose

Defines typed metadata flags stored in `cmds.Extra` to influence command pre-hooks and repo/config usage.

## Important APIs, Types, and Functions

`CreateCmdExtras` builds an extra value from option functions. `SetDoesNotUseRepo`/`GetDoesNotUseRepo`, `SetDoesNotUseConfigAsInput`/`GetDoesNotUseConfigAsInput`, and `SetPreemptsAutoUpdate`/`GetPreemptsAutoUpdate` manage boolean flags. `getBoolFlag` is the shared extractor.

## Control Flow

Setter functions close over a typed zero-size key and call `Extra.SetValue`. Getter functions retrieve with the same key and type assert the stored value to bool.

## State and Persistence Behavior

Only in-memory command metadata is affected. No repo state is read or written.

## Dependencies and Integration Points

Depends on `go-ipfs-cmds`. Used across command definitions for repo-independent commands such as `cid`, `commands`, and recovery commands.

## Risks and Edge Cases

`getBoolFlag` type asserts without checking the value type; only the paired setters should store these keys. Misusing key types or direct `Extra.SetValue` can panic.

## Test Signals

No direct tests. Command behavior indirectly depends on these flags in pre-hook code outside this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/extra.go -->
