# sources/distributed-fs/openafs/src/venus/test/idtest.c

## Purpose
`idtest.c` is a tiny identity diagnostic that prints the process effective UID and real UID. In the Venus test directory it helps check setuid, credential, or execution-context behavior on an AFS-mounted path.

## Important APIs, Types, And Functions
The only function is `main`. It calls `geteuid`, `getuid`, prints both integer values, and exits 0.

## Control Flow
The program ignores arguments. It reads and prints the effective UID first, then the real UID, then terminates with `exit(0)`.

## State And Persistence
The program is purely observational. It creates no files, changes no credentials, and writes only stdout.

## Dependencies And Integration Points
It depends only on standard Unix identity APIs plus OpenAFS build configuration headers. Within OpenAFS testing, it can be installed or executed with specific mode bits to observe whether AFS client and host policy honor effective-ID transitions.

## Risks And Test Signals
Risks are minimal; output formatting is fixed and no errors are possible from the two calls in normal POSIX environments. Useful signals are matching or intentionally different real/effective UID values under normal, setuid, and AFS `setcell` suid-policy scenarios.
