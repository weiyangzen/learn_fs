# sources/distributed-fs/ceph-client/include/dt-bindings/input/ti-drv260x.h

## Purpose
defines small input-subsystem binding constants for ti drv260x, such as key wakeup policy, GPIO key type selection, or haptic effect/library ids.

## Important APIs, Types, and Functions
The exported macros are `DRV260X_LRA_MODE`, `DRV260X_LRA_NO_CAL_MODE`, `DRV260X_ERM_MODE`, `DRV260X_LIB_EMPTY`, `DRV260X_ERM_LIB_A`, `DRV260X_ERM_LIB_B`, `DRV260X_ERM_LIB_C`, `DRV260X_ERM_LIB_D`, and 3 more. numeric values span 0..7 across 11 direct numeric defines.

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
