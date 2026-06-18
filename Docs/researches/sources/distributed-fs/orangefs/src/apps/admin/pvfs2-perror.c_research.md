# sources/distributed-fs/orangefs/src/apps/admin/pvfs2-perror.c

Purpose: `pvfs2-perror.c` is a small diagnostic utility that translates a numeric OrangeFS/PVFS error code into the standard `PVFS_perror` message.

Important APIs, types, and functions: `struct options` stores one `error_code`. `parse_args` accepts `-v` for version and `-h` for help, requires exactly one positional integer, and parses it with `sscanf`. `main` prints `Error code N` and calls `PVFS_perror("", -N)`. The only OrangeFS dependency is `pvfs2.h` for `PVFS_perror` and version wiring.

Control flow: main delegates all validation to `parse_args`. Help and version exit directly. If parsing succeeds, the utility prints to stderr and returns success. The input sign convention is inverted before calling `PVFS_perror`, so users enter positive errno-like numbers while the OrangeFS API receives negative PVFS status codes.

State and persistence: no state is read or written except command-line input and stderr output.

Dependencies and integration points: this is useful in scripts and admin sessions that receive numeric negative PVFS return values. It depends on the library error table compiled into the OrangeFS client library.

Risks: allocated options are not freed, though the process is short-lived. The usage text does not explain sign convention. `sscanf("%d")` accepts prefixes such as `12abc` as valid. It prints to stderr even on normal diagnostic success, which is conventional for `perror` but can surprise scripts.

Test signals: verify `-h`, `-v`, missing argument, extra arguments, nonnumeric input, positive values matching known PVFS errors, and behavior if users pass an already-negative code.
