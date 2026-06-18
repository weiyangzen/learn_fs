# sources/distributed-fs/ceph-client/drivers/input/mouse/byd.h

## Purpose

`byd.h` is the small private header that exposes the BYD PS/2 touchpad protocol hooks to psmouse core and the directory build. It keeps BYD detection and initialization declarations separate from `byd.c`.

## Important APIs, Types, and Functions

The header declares `int byd_detect(struct psmouse *psmouse, bool set_properties);` and `int byd_init(struct psmouse *psmouse);`. It also provides the `_BYD_H` include guard. `struct psmouse` is expected to be visible from the includer; `byd.c` includes `psmouse.h` before this header.

## Control Flow

There is no executable control flow. psmouse core calls `byd_detect()` during protocol probing, and if accepted calls `byd_init()` to install BYD-specific packet handling and input capabilities.

## State and Persistence Behavior

The header defines no state. Runtime state lives in `struct byd_data` in `byd.c` and is attached to `psmouse->private`.

## Dependencies and Integration Points

It integrates `byd.c` with the psmouse protocol selection code and the composite `psmouse.o` build. Any signature change here must match psmouse callers and `byd.c`.

## Risks and Edge Cases

Because the header does not forward-declare `struct psmouse` or include `<linux/types.h>` for `bool`, it relies on include ordering. That is fine for current local use but fragile if included from another context.

## Test Signals

Build coverage with `CONFIG_MOUSE_PS2_BYD=y/m` is the main signal. Compile errors would catch signature drift or missing include context.
