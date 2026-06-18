# sources/cloud-native/buildkit/cache/contenthash/path.go

Purpose: root-confined symlink-aware path resolution used by contenthash scans. It is adapted from `filepath-securejoin` with a callback for discovered symlinks.

Important APIs/types/functions: `errTooManyLinks`, `maxSymlinkLimit`, `onSymlinkFunc`, and `rootPath`.

Control flow: `rootPath` iteratively consumes path components, strips Windows volume names, handles lexical `.`/`..`, optionally avoids following the trailing symlink, reads symlink destinations, invokes the callback, prepends symlink targets to the remaining path, resets on absolute symlinks, and aborts after 255 links. It finally joins the resolved absolute-in-root path back under `root`.

State and persistence behavior: no persistent state. `scanPath` uses the callback to insert symlink `CacheRecord`s into the radix tree while resolving scan targets.

Dependencies and integration points: uses `os.Readlink`, filepath operations, and shared symlink limit/error used by `checksum.go`.

Risks: this is security-sensitive: mistakes can escape the mount root or mishandle non-lexical symlink paths. `followTrailing` must match checksum semantics for symlink final components.

Test signals: `path_test.go` exhaustively checks relative, absolute, nested, parent-directory, trailing, and Windows-adjusted symlink cases.
