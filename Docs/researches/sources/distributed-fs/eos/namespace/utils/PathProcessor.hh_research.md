# sources/distributed-fs/eos/namespace/utils/PathProcessor.hh

## Purpose
Collects path-splitting and absolute-path normalization helpers used by EOS namespace implementations. It bridges newer `StringSplit`-based path parsing with an older in-place splitter still used by the in-memory namespace backend.

## Important APIs, types, and functions
`insertChunksIntoDeque(std::string_view)` returns a deque of path components. The overload taking an existing deque prepends new path chunks while preserving component order. `splitPath(std::vector<char*>&, char*)` destructively splits a mutable C buffer by replacing slashes with null terminators. `absPath(std::string&)` normalizes `.` and `..` components into an absolute path.

## Control flow
Modern split helpers delegate to `eos::common::SplitPath`. The destructive splitter walks each character and records non-empty component starts. `absPath()` scans components from right to left, counts `..` skips, drops `.`, rebuilds with leading slashes, and returns `/` when all components collapse.

## State and persistence
No state is stored. `splitPath()` mutates its input buffer, so callers lose the original path string.

## Dependencies and integration points
Uses `common/StringSplit.hh` and standard containers. It is used by namespace views, path traversal, and legacy in-memory namespace code.

## Risks and test signals
Normalization does not preserve leading `..` above root, intentionally collapsing to root. Tests should cover repeated slashes, relative inputs, empty strings, trailing slashes, `.` and `..` combinations, destructive splitting side effects, and prepend order when an existing deque is non-empty.
