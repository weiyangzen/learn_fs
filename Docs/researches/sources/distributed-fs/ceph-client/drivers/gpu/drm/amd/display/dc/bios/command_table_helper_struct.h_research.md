# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/command_table_helper_struct.h

## Purpose
This header defines `struct command_table_helper`, the function-pointer vtable used by both legacy and firmware command-table implementations to convert DC abstractions into ATOM/firmware encodings.

## Important APIs, Types, And Functions
The struct contains callbacks for controller IDs, encoder actions/modes/IDs, engine IDs, control parameter assignment, PLL/ref-clock IDs, transmitter IDs, PHY IDs, signal modes, HPD selection, DIG encoder selection, power-gating actions, DCE clock types, and transmitter color depth.

## Control Flow
The header defines a dispatch contract only. DCE-family helper source files instantiate static const tables that fill appropriate callbacks.

## State And Persistence
Static instances of this struct are selected during BIOS parser initialization and stored through `bp->cmd_helper`. The pointed-to table is immutable.

## Dependencies And Integration Points
It includes DCE helper headers and forward-declares the legacy DIG encoder parameter type. It is shared by command-table helpers and command-table implementations.

## Risks
Several callbacks may be `NULL` for DCE generations that do not need them. Command-table code must only call callbacks guaranteed by the active helper table and command revision. Any struct layout change affects both legacy and firmware helper providers.

## Test Signals
Compile coverage catches missing members in designated initializers. Runtime validation should exercise command paths that use every non-NULL callback for each supported DCE/DCN family.
