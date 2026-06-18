# sources/distributed-fs/openafs/src/kauth/kkids.h

## Purpose
Declares the `kpasswd` password-validator child-process interface implemented by `kkids.c`.

## Important APIs, Types, And Functions
The exported functions are `init_child`, `password_bad`, `give_to_child`, and `terminate_child`.

## Control Flow
The intended flow is: initialize the child with the program name, send the old password, check candidate new passwords with `password_bad`, and terminate the child before exit.

## State And Persistence
The header stores no state. The implementation maintains process and pipe state.

## Dependencies And Integration Points
It is included by `kpasswd.c` and provides the only public interface to optional `kpwvalid` policy checks.

## Risks And Test Signals
Risks are prototype drift and missing cleanup in callers. Build coverage of `kpasswd` and runtime validation with and without `kpwvalid` are the test signals.
