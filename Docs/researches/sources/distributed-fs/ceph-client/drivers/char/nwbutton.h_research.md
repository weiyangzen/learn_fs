# sources/distributed-fs/ceph-client/drivers/char/nwbutton.h

## Purpose
`nwbutton.h` is the private/public header for the NetWinder button driver. When included by `nwbutton.c` with `__NWBUTTON_C` defined, it provides driver constants, callback structure definition, and internal prototypes. For other users it exposes the callback add/delete APIs.

## Important APIs, Types, and Functions
- `NUM_PRESSES_REBOOT` defines the reboot trigger count default as `2`.
- `BUTTON_DELAY` defines the sequence timeout as `30` jiffies.
- `VERSION` identifies the driver as `"0.3"`.
- `struct button_callback` stores a callback pointer and the press count that triggers it.
- External declarations expose `button_add_callback(void (*callback)(void), int count)` and `button_del_callback(void (*callback)(void))`.

## Control Flow
The header has two modes. In implementation mode it declares static internal functions and constants used by `nwbutton.c`. In external mode it hides internals and only declares the two callback registration functions.

## State and Persistence
The header defines structure shape and constants but stores no state. Runtime state lives in `nwbutton.c`'s static globals.

## Dependencies and Integration Points
It is included by the NetWinder button driver and any kernel code that wants to register callbacks for button sequences. The split declaration model depends on `nwbutton.c` defining `__NWBUTTON_C` before inclusion.

## Risks
- Internal static prototypes in a header are unusual and tightly couple the header to one C file.
- No locking contract is documented for callback registration, even though `nwbutton.c` uses a shared static callback array.
- Constants are compile-time only; changing behavior requires rebuilding.

## Test Signals
Tests are indirect through `nwbutton.c`: build coverage should confirm implementation and external include modes compile, and callback users should link against the external declarations without seeing internal symbols.
