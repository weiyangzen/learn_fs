# sources/distributed-fs/openafs/src/WINNT/tests/winflock/winflock.h

Purpose: shared declarations and synchronization macros for the WinFLock test program.

Important APIs and types: includes Win32, TCHAR, iostream, assert, and `strsafe.h`; declares global test directory and synchronization handles; maps `logfile` to `cout`; declares all test functions; defines `PAGE_BEGIN` and `PAGE_LEN` for 4 KiB page ranges.

Control flow: macros `BEGINLOG`/`ENDLOG`, `SYNC_BEGIN_PARENT`/`SYNC_END_PARENT`, and `SYNC_BEGIN_CHILD`/`SYNC_END_CHILD` hide the event/mutex protocol implemented in `sync.cpp`.

State and persistence: no storage itself, but exposes shared globals defined in `main.cpp` and `tests.cpp`.

Dependencies and integration: included by all WinFLock translation units. Test function prototypes match the sequence in `run_tests`.

Risks and test signals: the synchronization macros rely on brace-style use and are easy to misuse. Because `logfile` is `cout`, mutex protection only serializes cooperating process output to the console stream.
