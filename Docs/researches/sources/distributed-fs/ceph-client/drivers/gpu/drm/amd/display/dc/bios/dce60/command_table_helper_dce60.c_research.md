# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/dce60/command_table_helper_dce60.c

## Purpose
This file provides the command-table helper vtable for SI/DCE6 display hardware.

## Important APIs, Types, And Functions
- `dal_cmd_tbl_helper_dce60_get_table()` returns the DCE60 helper table.
- Static mappings translate encoder actions, clock sources, signal DIG modes, HPD selection, DIG encoder selection, and display power-gating actions.
- The table uses legacy shared helpers for controller, engine, ref-clock, transmitter, encoder ID, encoder mode, PHY, and DIG control parameter packing.

## Control Flow
The mapping logic mirrors DCE80-era V5 ATOM transmitter fields. `dig_encoder_sel_to_atom()` maps DIGA through DIGG to explicit `ATOM_TRANMSITTER_V5__DIG*` selections, unlike DCE110+ where this returns zero.

## State And Persistence
The helper table is immutable and has no mutable runtime state.

## Dependencies And Integration Points
It depends on `atom.h`, graph object headers, BIOS parser types, and the shared legacy helper. It is selected only when `CONFIG_DRM_AMD_DC_SI` enables SI support.

## Risks
Unsupported values often break to debugger and then return default ATOM selections, especially DVI/DIGA defaults. Because SI support is conditional, build/test coverage may be absent in some kernels.

## Test Signals
SI display bring-up, DP/eDP/DVI/HDMI mode programming, HPD routing, DIG FE selection, and VBIOS command traces are the primary validation signals.
