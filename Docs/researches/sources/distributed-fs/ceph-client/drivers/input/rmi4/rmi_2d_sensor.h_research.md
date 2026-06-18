<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_2d_sensor.h -->
# sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_2d_sensor.h

## Purpose
`rmi_2d_sensor.h` defines the shared 2D sensor object model and helper API used by RMI4 pointing functions.

## Important APIs, Types, and Functions
`enum rmi_2d_sensor_object_type` classifies none, finger, stylus, palm, and unclassified objects. `struct rmi_2d_sensor_abs_object` stores transformed/reportable object fields. `struct rmi_2d_sensor` stores axis alignment, tracking arrays, packet buffers, dimensions, finger counts, input pointers, report flags, physical sizes, and register-state preferences. The header declares the exported helper functions from `rmi_2d_sensor.c`.

## Control Flow
The header has no executable path. Function drivers instantiate `struct rmi_2d_sensor`, fill it from query/platform data, configure input, then use the process/report helpers during attention interrupts.

## State and Persistence
The declared structs hold per-function runtime state and static platform-derived configuration while the function is bound.

## Dependencies and Integration Points
It depends on `linux/rmi.h`, Linux integer types, and `struct rmi_function`. It is consumed by RMI4 F11/F12 and any other 2D pointing functions.

## Risks and Edge Cases
The structure contains raw pointers (`tracking_pos`, `tracking_slots`, `objs`, `data_pkt`) whose allocation and lifetime are owned by function drivers. Mismatched `nbr_fingers`, packet sizes, and tracking arrays can cause reporting errors.

## Test Signals
Compile and runtime validation through F11/F12 handlers should confirm object type mapping, slot counts, and property-driven axis behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_2d_sensor.h -->
