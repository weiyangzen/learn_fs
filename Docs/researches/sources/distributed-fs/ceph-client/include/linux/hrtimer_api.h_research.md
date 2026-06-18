# sources/distributed-fs/ceph-client/include/linux/hrtimer_api.h

## Purpose
`hrtimer_api.h` is a compatibility/convenience shim that includes `linux/hrtimer.h`. It provides no independent API beyond re-exporting the main hrtimer declarations.

## Important APIs, Types, And Functions
There are no local types or functions. Including this header is equivalent to including `linux/hrtimer.h`.

## Control Flow And State
There is no control flow or state in this file. All behavior comes from `hrtimer.h` and its included support headers.

## Dependencies And Integration Points
It depends directly on `linux/hrtimer.h`. It exists for include-path compatibility with code that expects an `hrtimer_api.h` name.

## Risks
The only practical risk is include recursion or unnecessary layering if hrtimer headers are reorganized. Removing it can break source compatibility for existing include users.

## Test Signals
Build all users that include `linux/hrtimer_api.h` and verify they see the same hrtimer symbols as direct `linux/hrtimer.h` users.
