<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/vmmouse.h -->
# sources/distributed-fs/ceph-client/drivers/input/mouse/vmmouse.h

## Purpose
`vmmouse.h` exposes the VMware virtual PS/2 mouse protocol hooks to the psmouse core.

## Important APIs, Types, and Functions
It defines `VMMOUSE_PSNAME` and declares `vmmouse_detect()` and `vmmouse_init()`.

## Control Flow
No runtime flow is implemented here; the psmouse probe path uses the declarations to detect and initialize the vmmouse protocol.

## State and Persistence
The header declares no state.

## Dependencies and Integration Points
The prototypes depend on `struct psmouse` and are implemented by `vmmouse.c`. The header belongs to the psmouse protocol integration layer.

## Risks and Edge Cases
The interface is intentionally narrow. Any future vmmouse feature requiring shared state should remain in `vmmouse.c` unless the psmouse core needs to see it.

## Test Signals
Compile coverage of psmouse protocol selection and successful vmmouse detection/initialization provide validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/vmmouse.h -->
