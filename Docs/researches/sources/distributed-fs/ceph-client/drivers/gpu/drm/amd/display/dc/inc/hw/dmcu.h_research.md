# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/dmcu.h

## Purpose

`dmcu.h` defines the Display Microcontroller Unit abstraction used for firmware-managed display features such as PSR, ABM-related firmware state, EDID/VSDB messaging, PHY locks, and optional secure-display CRC window forwarding.

## Important APIs, Types, And Functions

Important types include `enum dmcu_state`, `struct dmcu_version`, `struct dmcu`, and `struct dmcu_funcs`. Operations include `dmcu_init`, `load_iram`, PSR enable/setup/state/wait-loop accessors, initialization check, PHY lock/unlock, EDID CEA send/ack, AMD VSDB receive, and secure-display CRC window controls when configured.

## Control Flow

Firmware load/init moves the DMCU from unloaded or loaded-uninitialized to running. PSR setup programs link/context data, then enable/disable and state queries control panel self refresh. EDID/VSDB helper calls exchange data through firmware. PHY lock/unlock gates sensitive link/PHY access.

## State And Persistence Behavior

`dmcu` persists as a resource object with context, vtable, state, firmware version, cached wait-loop number, PSP version, and auto-load flag. Firmware state persists in DMCU memory/hardware until reset or reloaded. There is no disk persistence.

## Dependencies And Integration Points

It includes service types and forward-referenced DC link/PSR/rect/mux types. It integrates with ABM, PSR, eDP/panel features, PSP firmware loading, secure display, and HWSS/panel power sequencing.

## Risks And Edge Cases

The state machine requires correct transition checks: some init commands are valid only when firmware is loaded but uninitialized. Firmware version compatibility affects PSR/ABM commands. PHY locks must be released. Optional secure-display callbacks depend on kernel config and mux mapping validity.

## Test Signals

Tests should cover firmware load/init, auto-load, PSR setup/enable/disable/state transitions, wait-loop persistence, EDID/VSDB messaging, PHY lock/unlock error paths, suspend/resume, and secure-display CRC forwarding. Firmware command timeouts and PSR entry/exit failures are key signals.
