# sources/distributed-fs/ceph-client/include/dt-bindings/input/linux-event-codes.h

## Purpose
exposes Linux input event, key, relative/absolute axis, switch, LED, sound, force-feedback, and property code constants to Devicetree users through the dt-bindings input symlink.

## Important APIs, Types, and Functions
The API is the full UAPI input-event code namespace: 795 macros such as `INPUT_PROP_POINTER`, `INPUT_PROP_DIRECT`, `INPUT_PROP_BUTTONPAD`, `INPUT_PROP_SEMI_MT`, `INPUT_PROP_TOPBUTTONPAD`, `INPUT_PROP_POINTING_STICK`, `INPUT_PROP_ACCELEROMETER`, `INPUT_PROP_PRESSUREPAD`, `INPUT_PROP_MAX`, `INPUT_PROP_CNT`. This path is a symlink to `sources/distributed-fs/ceph-client/include/uapi/linux/input-event-codes.h` and carries the same ABI as the kernel UAPI header.

## Control Flow
There is no executable flow. DTS files include the dt-bindings path for keymaps or GPIO-key codes; the compiler emits numeric event codes; input drivers report those codes through the Linux input subsystem.

## State, Persistence, and Dependencies
The header is immutable ABI data. Persistence is through compiled DTBs and userspace-visible event codes; values must match UAPI expectations. It depends on the UAPI input-event namespace and is consumed by keyboard matrices, GPIO keys, EC keyboards, touch/buttons, and any DT binding that names Linux input codes.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
Any divergence from UAPI, broken symlink handling in source packaging, or use of unsupported event codes can break key reporting or userspace input interpretation.

## Test Signals
Compile DTS keymaps that include this path, compare representative constants against UAPI values, and exercise input drivers to confirm emitted EV_KEY/EV_ABS/etc. codes.
