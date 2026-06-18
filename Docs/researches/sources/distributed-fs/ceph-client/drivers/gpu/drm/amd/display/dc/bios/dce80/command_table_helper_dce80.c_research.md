# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/dce80/command_table_helper_dce80.c

## Purpose
This file provides the helper vtable for DCE8 display hardware, using V5 ATOM transmitter encodings.

## Important APIs, Types, And Functions
- `dal_cmd_tbl_helper_dce80_get_table()` returns the static helper table.
- Static mapping functions cover encoder action, clock source, signal mode, HPD selection, DIG encoder selection, and display power gating.
- It reuses shared helpers for controller, engine, DIG control packing, ref-clock, transmitter, encoder ID, encoder mode, PHY ID, and PHY clock source mapping.

## Control Flow
The control flow is switch-based enum translation. DIG encoder selection explicitly maps DIGA-DIGG to V5 transmitter FE selection constants.

## State And Persistence
No mutable state exists. The returned helper table is static const data.

## Dependencies And Integration Points
It depends on `atom.h`, graph object headers, BIOS parser types, and `command_table_helper.h`. It is selected for DCE8.0, DCE8.1, and DCE8.3.

## Risks
DCE60 and DCE80 helper code is nearly identical, so fixes can diverge if applied to one copy only. Unsupported inputs fall back to defaults after debugger breaks.

## Test Signals
Validate on DCE8 ASICs with DP, HDMI, DVI, LVDS/eDP, and MST paths, checking VBIOS command parameters and display light-up.
