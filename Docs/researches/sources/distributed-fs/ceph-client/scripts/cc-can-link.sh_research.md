# sources/distributed-fs/ceph-client/scripts/cc-can-link.sh

## Purpose
`cc-can-link.sh` checks whether a compiler command can link a minimal C program without warnings treated as nonfatal.

## APIs, Types, And Functions
The shell script feeds a tiny C program to `$@` with `-Werror`, `-Wl,--fatal-warnings`, `-x c -`, and output `/dev/null`.

## Control Flow
It writes source through a here-document into the provided compiler command. Success or failure is the compiler/linker exit status.

## State And Persistence
No state is stored. Temporary compiler outputs target `/dev/null`.

## Dependencies And Integration Points
It depends on the caller passing a complete compiler command and linker accepting the options. It integrates with kbuild toolchain capability checks.

## Risks And Test Signals
Risks include compilers that do not accept GNU-style flags or wrappers that mishandle stdin. Test signal is exit 0 for a working native/cross linker and nonzero for compile-only or broken link setups.
