# sources/distributed-fs/orangefs/src/client/windows/client-test/find.h

## Purpose
`find.h` declares Windows-only find/enumeration tests.

## Important APIs, Types, And Functions
When `WIN32` is defined, it includes `test-support.h` and declares `find_files` and `find_files_pattern`.

## Control Flow
`test-list.h` registers these functions only for Windows builds. Non-Windows builds see no test declarations.

## State And Persistence
The header defines no state. Runtime file creation and cleanup are in `find.c`.

## Dependencies And Integration Points
The Windows-only guard matches the implementation’s use of CRT `_findfirst` APIs. These tests integrate with the Dokany directory enumeration path.

## Risks And Test Signals
Because declarations vanish on non-Windows builds, build coverage differs by platform. The Makefile for the Linux-style build does not include `find.o`, consistent with the guard.
