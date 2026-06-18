<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/touchkit_ps2.h -->
# sources/distributed-fs/ceph-client/drivers/input/mouse/touchkit_ps2.h

## Purpose
`touchkit_ps2.h` is the minimal interface header for the eGalax TouchKit PS/2 touchscreen protocol.

## Important APIs, Types, and Functions
It declares `touchkit_ps2_detect(struct psmouse *psmouse, bool set_properties)`, which is implemented in `touchkit_ps2.c` and called by psmouse protocol probing.

## Control Flow
The header has no runtime control flow; it allows the psmouse core to invoke detection and optional property setup.

## State and Persistence
No state is declared here.

## Dependencies and Integration Points
The prototype depends on `struct psmouse` and the boolean type being visible to including files. Its integration point is the PS/2 mouse protocol dispatcher.

## Risks and Edge Cases
The header is intentionally narrow. Any additional TouchKit protocol state would need a corresponding psmouse-private structure and lifecycle handling in the implementation.

## Test Signals
Compile-time coverage of the psmouse protocol table is the main signal; runtime behavior is validated through `touchkit_ps2.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/touchkit_ps2.h -->
