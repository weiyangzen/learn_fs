# File Research: sources/cow-pools/bcachefs-tools/fs/snapshots/subvolume.h

Public subvolume API and bkey ops. It declares checkers, validation/text/trigger functions, child detection, subvolume lookup, snapshot ID lookup, read-only checks, unlink/create/init/upgrade entry points, and early init.

Provides iterator helpers/macros for reading btree keys within a subvolume by lazily resolving the subvolume’s snapshot ID and setting the iterator snapshot, with transaction-restart handling variants.
