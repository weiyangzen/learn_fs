# sources/distributed-fs/eos/unit_tests/mgm/FileSystemRegistryTests.cc

## Purpose
Tests `FileSystemRegistry`, the MGM utility that maps filesystems by id, pointer, and queue path. It verifies duplicate prevention and cleanup of all lookup indexes.

## Important APIs, types, and functions
The tests use `FileSystemRegistry::registerFileSystem`, `lookupByID`, `lookupByPtr`, `lookupByQueuePath`, `eraseById`, `eraseByPtr`, `clear`, and `size`, with `FileSystemLocator` values and dummy `FileSystem*` pointers.

## Control flow
The basic test registers a locator/id/pointer triple, rejects duplicates by locator/id/pointer combinations, validates each lookup path, erases entries by id and pointer, and clears the registry. The queue-path collision test ensures one queue path cannot be registered twice under different ids.

## State and persistence
All registry state is in-memory. The registry mirrors production MGM filesystem inventory and must keep multiple indexes consistent.

## Dependencies and integration points
Depends on Google Test, `mgm/utils/FileSystemRegistry.hh`, and common filesystem locator formatting. It integrates with FsView/filesystem management code.

## Risks and test signals
Tests provide good index-consistency signals. Risks not covered include concurrent registration/erase, null pointer registration policy beyond lookup, and filesystem locator normalization differences. Queue path formatting is part of the compatibility surface.
