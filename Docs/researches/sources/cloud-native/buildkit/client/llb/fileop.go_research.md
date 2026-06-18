# sources/cloud-native/buildkit/client/llb/fileop.go

Purpose: implements LLB file operations and fluent `FileAction` builders for directory creation, file creation, symlinks, removals, and copies.

Important APIs/types/functions: `NewFileOp` binds actions to a base state. `FileAction` chains actions through `prev`, supports `Mkdir`, `Mkfile`, `Symlink`, `Rm`, `Copy`, `WithState`, and output discovery. Action implementations include `fileActionMkdir`, `fileActionMkfile`, `fileActionSymlink`, `fileActionRm`, and `fileActionCopy`. Option structures include `MkdirInfo`, `MkfileInfo`, `SymlinkInfo`, `RmInfo`, `CopyInfo`, `ChownOpt`, `ChmodOpt`, and `CreatedTime`. `marshalState` linearizes action graphs and assigns base/primary/secondary/relative inputs.

Control flow: public helpers build immutable-looking linked action nodes. `State.File` binds an action chain to a state and creates a `FileOp`. During marshal, file op validates action presence, derives platform from base but clears platform on the file op itself, collects all input outputs, recursively adds action states, deduplicates protobuf inputs, converts each action to protobuf with normalized paths and owner/timestamp data, assigns skipped output to intermediate actions and output zero to the final action, serializes deterministically, and caches.

State and persistence: no external persistence; file changes are declarative LLB actions executed by solver workers. Internally, `FileAction.bind` shallow-copies chains with bound state; `marshalState` tracks visited actions to avoid duplicate action expansion; `FileOp` stores marshal cache and validation state.

Dependencies/integration points: state metadata for working directories/platforms, solver protobuf file actions, capabilities for symlink/copy patterns/required paths/replace/mode string, `path` normalization, and file/action tests.

Risks/test signals: capability detection currently iterates `state.actions` before `state.add(f.action, c)`, so cap adders may not be applied at that moment; solver compatibility for newer file features depends on correct caps. `fileActionCopy.addCaps` dereferences `a.info.Mode.ModeStr` without nil guarding, though the method is only useful when reached. Path normalization and relative action indexes are subtle. Extensive tests in `fileop_test.go` cover action shapes, owner handling, timestamps, action-copy pipelines, deterministic marshaling, and parallel marshaling.
