<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/check-exec/inc.c -->
# sources/distributed-fs/ceph-client/samples/check-exec/inc.c

## Purpose
`inc.c` is a tiny script interpreter used to demonstrate and test exec-check securebits. It interprets line-oriented `?` and `+` commands from a file, stdin, or `-c` command string while consulting kernel `AT_EXECVE_CHECK` policy.

## Important APIs, Types, And Functions
Important routines are `sys_execveat()`, `interpret_buffer()`, `interpret_stream()`, `print_usage()`, and `main()`. It uses `prctl(PR_GET_SECUREBITS)`, `SECBIT_EXEC_DENY_INTERACTIVE`, `SECBIT_EXEC_RESTRICT_FILE`, `execveat(AT_EMPTY_PATH | AT_EXECVE_CHECK)`, `fread()`, `strtok_r()`, and `scanf()`.

## Control Flow
`main()` reads current securebits, parses `-c`, `-i`, or script path mode, and enforces that exactly one interpretation source is used. Command-string mode is denied when interactive interpretation is denied. Stdin mode treats `/proc/self/fd/0` as the script name and restricts based on interactive policy. File mode opens the script and restricts based on file policy. `interpret_stream()` asks the kernel to check execution permission on the script fd, then reads and interprets up to 127 bytes. The interpreter increments/prints a counter for `+` and reads a new number for `?`.

## State And Persistence
Process state includes current counter value, securebit-derived booleans, script stream, and input buffer. Securebits are inherited from the launcher and are not changed here.

## Dependencies And Integration Points
It depends on new securebits and `AT_EXECVE_CHECK` kernel support, UAPI headers, and the `set-exec` wrapper. It is referenced by the scripts and selftest documentation.

## Risks And Edge Cases
Only a small fixed buffer is read from scripts, so longer scripts are truncated. Command validation only accepts single-character commands or comments. Kernels lacking the feature cause check errors only when restrictive mode requires them.

## Test Signals
Executable scripts should run under allowed policy. `-c` or stdin should be rejected when `SECBIT_EXEC_DENY_INTERACTIVE` is locked. Non-executable/restricted files should fail when `SECBIT_EXEC_RESTRICT_FILE` applies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/check-exec/inc.c -->
