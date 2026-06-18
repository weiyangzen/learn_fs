# sources/distributed-fs/ceph-client/include/dt-bindings/input/cros-ec-keyboard.h

## Purpose
defines ChromeOS EC keyboard matrix position macros and function-row aliases used by Devicetree keymap descriptions.

## Important APIs, Types, and Functions
The exported macros include `CROS_STD_TOP_ROW_KEYMAP`, `CROS_STD_MAIN_KEYMAP`, `CROS_TOP_ROW_KEYMAP_V30`, `CROS_MAIN_KEYMAP_V30`; many values are `MATRIX_KEY(row, col, code)` expressions tying matrix coordinates to Linux key codes.

## Control Flow
No code runs here. DTS keymap nodes expand these macros into packed matrix entries, and the cros-ec keyboard/input driver later scans EC matrix events and reports the mapped Linux key code.

## State, Persistence, and Dependencies
No state is stored. The durable contract is the matrix coordinate and key-code layout in board DTBs. It includes or relies on `input.h`/Linux event-code definitions and integrates with ChromeOS EC keyboard bindings and matrix-keymap parsing.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
Wrong row/column aliases or stale key-code constants produce swapped keys. Matrix-size changes must stay aligned with EC firmware and board wiring.

## Test Signals
DTS compile coverage, matrix-keymap parser tests, and board keyboard smoke tests should validate representative alphanumeric, function, and special keys.
