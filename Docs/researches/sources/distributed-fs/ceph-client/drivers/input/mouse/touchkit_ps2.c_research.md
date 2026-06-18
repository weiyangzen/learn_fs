<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/touchkit_ps2.c -->
# sources/distributed-fs/ceph-client/drivers/input/mouse/touchkit_ps2.c

## Purpose
`touchkit_ps2.c` detects and drives eGalax TouchKit PS/2 touchscreens. It configures the psmouse instance as a five-byte absolute touchscreen protocol and reports X/Y plus touch state.

## Important APIs, Types, and Functions
The exported function is `touchkit_ps2_detect()`. Packet parsing happens in `touchkit_ps2_process_byte()`. Macros define maximum coordinates, command framing, active-controller query values, and packet field extraction for touch, X, and Y.

## Control Flow
Detection sends a vendor command using `ps2_command()` and verifies the returned command byte, length/status byte, and active command echo. If `set_properties` is true, the function rewrites input capabilities to key/absolute only, sets `BTN_TOUCH`, configures `ABS_X` and `ABS_Y` to 0..0x07ff, sets psmouse vendor/name, assigns the protocol handler, and sets packet size to five. The handler waits until `pktcnt == 5`, reports decoded X/Y/touch, syncs, and returns `PSMOUSE_FULL_PACKET`.

## State and Persistence
No private allocation is used. State is stored in the shared `psmouse` fields and the packet buffer while the protocol is active.

## Dependencies and Integration Points
The driver uses the psmouse/libps2 serio framework and Linux input absolute/key reporting. It is included by the PS/2 mouse protocol selection machinery rather than registering a standalone module driver.

## Risks and Edge Cases
The protocol assumes fixed five-byte packets and does not perform additional packet validation beyond psmouse framing. Detection depends on a specific active command response; incompatible firmware may be rejected. The capability rewrite clears mouse key state and should only run after a positive detection.

## Test Signals
Detection should reject ordinary PS/2 mice and accept TouchKit hardware. `evtest` should show `ABS_X`, `ABS_Y`, and `BTN_TOUCH` only, with correct coordinate range and one sync per five-byte packet.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/touchkit_ps2.c -->
