# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-helper-board.c

## Purpose
Provides board-specific networking facts that generic chip probing cannot infer: PHY addresses, fallback link status, actual port counts, and USB clock type.

## Important APIs, Types, And Functions
Core functions are `cvmx_helper_board_get_mii_address()`, `__cvmx_helper_board_link_get()`, `__cvmx_helper_board_interface_probe()`, and `__cvmx_helper_board_usb_get_clock_type()`. They read `cvmx_sysinfo_get()->board_type` and selected GMX in-band status registers.

## Control Flow
PHY lookup is a board-type switch over known Octeon boards and IPD port ranges. Link lookup returns a simulated link, decodes in-band GMX status on supported older models, or reports down. Interface probe trims generic port counts for boards with unwired or unsupported interfaces.

## State, Persistence, And Dependencies
No private state is kept. Behavior depends on bootloader-populated sysinfo, board enums, helper port mapping, and GMX/ASX CSR correctness.

## Integration Points
Generic helper enumeration calls the board port-count override. RGMII/SGMII link getters use the board fallback when no proper PHY/device-tree status is available.

## Risks
Unknown boards report no PHY and print an error. Deprecated link fallback can be wrong and explicitly warns outside simulation. Bad table entries silently miswire ports.

## Test Signals
Exercise board/IPD mappings, simulation link behavior, in-band speed decoding, disabled-interface overrides, and USB clock decisions for exception boards.
