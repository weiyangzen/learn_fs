# sources/distributed-fs/openafs/src/dir/test/dtest.c

This userspace CLI exercises the directory package against flat files. Commands list (`-l`), check (`-c`), salvage (`-s`), create/fill (`-f`), delete (`-d`), lookup (`-r`), and add (`-a`) directory entries.

Important functions are command wrappers `LookupDir`, `AddEntry`, `ListDir`, `CheckDir`, `SalvageDir`, `DelTest`, `CRTest`; file helpers `OpenDir`/`CreateDir`; buffer backend callbacks `ReallyRead`, `ReallyWrite`, `FidZap`, `FidZero`, `FidEq`, `FidVolEq`, `FidCpy`; and diagnostic `Die`/`Log`. `main` initializes the directory buffer cache with 600 buffers and dispatches by the first option character.

State and persistence are test directory files opened with POSIX `open`, read/written in 2048-byte pages. `fidCounter` and `Uniq` provide simple unique ids in-process. Dependencies are `afs/dir.h`, `opr_abort`, file I/O, and varargs logging. Risks include simplistic fid equality by unique handle, no fsync, limited argument validation, and salvage continuing after failed dot lookups. Test signals are the command modes themselves and regression scripts that create, mutate, check, and salvage directory images.
