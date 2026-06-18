# sources/distributed-fs/openafs/src/WINNT/afsreg/test/dupkey.c

## Purpose
Small manual test program for `RegDupKeyAlt`. It duplicates one registry key tree to another and reports success or the Win32 error code.

## Important APIs, Types, And Functions
The only function is `main`, which validates that two key path arguments were supplied and calls `RegDupKeyAlt(argv[1], argv[2])`.

## Control Flow
Incorrect argument count prints `Usage: <program> key1 key2` and exits with status 1. Otherwise the program performs duplication and prints a success/failure message. The source and target key names are expected to be canonical paths accepted by `RegOpenKeyAlt`.

## State And Persistence
The program can modify persistent registry state by deleting/replacing the target key and copying source values/subkeys into it.

## Dependencies And Integration Points
It includes `WINNT/afsreg.h` and links against the registry helper implementation plus Win32 registry libraries. It is a developer/admin diagnostic rather than production code.

## Risks And Test Signals
Because target keys are replaced by `RegDupKeyAlt`, running it with real OpenAFS keys can be destructive. Useful test signals are success duplicating a temporary nested key and failure codes for missing source or inaccessible target.
