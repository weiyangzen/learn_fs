# sources/cloud-native/containers-storage/drivers/aufs/dirs.go

## Purpose
`dirs.go` centralizes AUFS directory and parent metadata helpers. It reads known layer IDs, parses parent chains, and constructs driver paths for mount and diff directories.

## Important APIs, Types, And Functions
`loadIds(root)` returns non-directory entries from the metadata directory, matching AUFS `layers/<id>` files. `getParentIDs(root, id)` reads non-empty lines from `layers/<id>`. `getMountpoint`, `mntPath`, `getDiffPath`, and `diffPath` build canonical paths from `Driver.rootPath`.

## Control Flow
Status calls `loadIds` to count layer metadata. Create/Get/Changes call `getParentIDs` to recover parent order. Path helpers are used by create, remove, mount, diff, and disk-usage methods.

## State And Persistence
The file reads persistent `layers/<id>` files but does not mutate state. Parent ordering is significant: the first line is the direct parent and following lines are older ancestors.

## Dependencies And Integration Points
It uses `os.ReadDir`, `os.Open`, `bufio.Scanner`, and `path.Join`. It is tightly coupled to the storage layout described in `aufs.go`.

## Risks
Malformed or missing `layers/<id>` files propagate errors or produce incorrect parent stacks. `loadIds` intentionally returns file names, not directories; changing that would break status counts.

## Test Signals
AUFS tests indirectly exercise these helpers via status counts, parent-aware mounts, invalid-parent create failures, and deep-layer construction.
