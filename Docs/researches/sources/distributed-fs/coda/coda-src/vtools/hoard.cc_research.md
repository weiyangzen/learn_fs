# sources/distributed-fs/coda/coda-src/vtools/hoard.cc

## Purpose

`hoard.cc` implements the Coda hoard database front-end. It parses user commands for hoard-priority entries and sends HDB pioctls to Venus to clear, add, delete, list, walk, verify, enable, or disable hoard database behavior.

## Important APIs, Types, and Functions

The file defines wrapper classes around HDB messages: `clear_entry`, `add_entry`, `delete_entry`, `listentry`, `walk_entry`, `enable_entry`, `disable_entry`, and `verify_entry`. `ParseCommandLine()` chooses command input from `-f`, stdin, or direct argv text. `ParseHoardCommands()` tokenizes and builds `olist` queues. `canonicalize()`, `vol_getwd()`, and `GetVid()` resolve paths to Coda volume id, realm, and volume-relative name. `MetaExpand()` and `ExpandNode()` expand children/descendants. `DoClears()`, `DoAdds()`, `DoDeletes()`, `DoLists()`, `DoWalks()`, `DoVerifies()`, `DoEnables()`, and `DoDisables()` execute pioctls. `RenameOutFile()` copies Venus output files to user targets under the real UID.

## Control Flow

Startup parses input, records cwd and uid, parses all commands into separate lists, initializes `venus.conf`, then executes lists in a fixed order: clear, add, delete, list, walk, verify, enable, disable. Parser commands support abbreviations: `clear`, `add`, `delete`, `list`, `walk`, `verify`, `on`, and `off`. Adds canonicalize the target, parse priority/attribute fields such as children/descendants/inherit, optionally meta-expand, and append symlink entries discovered during canonicalization.

## State and Persistence Behavior

Durable state changes are in Venus' hoard database through `_VIOC_HDB_*` pioctls. List and verify ask Venus to write temporary output files and then copy them to user-requested destinations. `walk`, `on`, and `off` affect hoard-walk execution. The tool changes directories during canonicalization and expansion but attempts to return to the original cwd.

## Dependencies and Integration Points

It depends on Coda `venusioctl.h`, `hdb.h`, `vice.h`, `codaconf.h`, `olist`, `pioctl`, `VolumeId`, `ViceFid`, and Coda symlink limits. It also depends on Unix process APIs, `cat`, real/effective uid behavior, and Coda mountpoint configuration.

## Risks

The code uses `tmpnam()` for output files, which is race-prone. Many `strcpy()`/`strcat()` operations assume `MAXPATHLEN` bounds. `canonicalize()` manually follows symlinks and can loop or overflow with hostile paths. `ExpandNode()` constructs `tname` for each child but recursively calls `ExpandNode(..., name, ...)` rather than `tname`, likely breaking descendant expansion and potentially recursing incorrectly. `RenameOutFile()` forks and execs `cat` instead of copying directly. Parser memory allocated with `new` is not released, acceptable for process lifetime but not reusable. Commands that partly fail continue, so batch updates can leave mixed HDB state.

## Test Signals

Tests should cover command parsing, priority/attribute combinations, canonicalization of absolute/relative paths and symlinks, volume-boundary detection, meta-expansion over children/descendants, HDB message packing, output copy failure paths, uid switching, and partial-failure behavior. Integration tests need a Coda mount and Venus HDB pioctl support.
