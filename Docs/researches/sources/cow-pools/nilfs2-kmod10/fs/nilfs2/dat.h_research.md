# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/dat.h

Public DAT interface. It declares translation, allocation/start/end/update prepare-commit-abort routines, dirty marking, batch free, GC move, vinfo export, and DAT inode read/init.

Integration: used by bmap direct/B-tree implementations, B-tree node cache reads, GC inode logic, and segment construction paths that assign or relocate blocks.

Risk/notes: the API is transactional and stateful; every prepare path has matching commit/abort expectations.
