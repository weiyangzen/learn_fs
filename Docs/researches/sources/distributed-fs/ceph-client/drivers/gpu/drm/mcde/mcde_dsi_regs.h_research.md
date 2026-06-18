## sources/distributed-fs/ceph-client/drivers/gpu/drm/mcde/mcde_dsi_regs.h

### Purpose

`mcde_dsi_regs.h` defines the MCDE DSI controller register map and bitfields used by the DSI host/bridge implementation.

### Important APIs, types, and functions

The header exports preprocessor constants for main data/PHY/enable/status registers, DPHY timeout/static/ULP timing, command-mode status/control, direct command send/read/write/status registers, TE and command-mode interrupt control/clear fields, video-mode main control, size/timing/blanking/VCA registers, DPHY lane trim, and ID/status registers.

### Control flow

There is no runtime flow. `mcde_dsi.c` composes these fields to start the link, issue direct MIPI commands, request TE, configure command/video modes, program video timing, enable errors, poll status, and clear latched IRQs.

### State and persistence behavior

The macros describe persistent DSI hardware state: link enable, lane count, continuous clocking, ULPM behavior, timeout values, direct-command payload/status, video packet layout, sync/blanking sizes, burst limits, and status interrupt masks. State remains until reset, power loss, or explicit rewrites.

### Dependencies

The header expects standard `BIT()` definitions and MIPI constants in consumers. Semantically it is tied to the ST-Ericsson MCDE DSI hardware.

### Integration points

It is included only by `mcde_dsi.c` and is the low-level contract between DSI host operations, video mode setup, TE handling, and MCDE display sequencing.

### Risks

Wrong masks or shifts can corrupt DSI command payloads or timing, producing panel hangs. Several fields are used in read-clear flows; incorrect clear bits can lose or retain interrupts. Video timing fields mix bytes, pixels, lanes, and clock cycles, so field naming alone is not enough to prevent misuse.

### Test signals

Signals include DSI register readback, command transfer success, TE status clear behavior, lane-ready polling, video-mode sync stability, burst/non-burst panels, and error interrupt injection or observation.
