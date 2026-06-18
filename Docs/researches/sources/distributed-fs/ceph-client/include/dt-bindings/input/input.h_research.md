# sources/distributed-fs/ceph-client/include/dt-bindings/input/input.h

## Purpose
defines small input-subsystem binding constants for input, such as key wakeup policy, GPIO key type selection, or haptic effect/library ids.

## Important APIs, Types, and Functions
The exported macros are `MATRIX_KEY`. 1 expression-valued defines are present.

## Control Flow
There is no executable flow; values are compiled into DTB properties and consumed by the matching input driver during probe.

## State, Persistence, and Dependencies
No state is kept in the header. The ABI values persist in DTBs and affect input device registration or event reporting. Integration is through input binding YAML, board DTS files, and Linux input drivers that translate the values into event types, key properties, or haptics modes.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
Numeric drift or missing validation can lead to wrong input event type, wake behavior, or haptic waveform selection.

## Test Signals
Run dtbs_check and probe the relevant input drivers with representative properties, confirming reported input capabilities and wake/haptic behavior.
