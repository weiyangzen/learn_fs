# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_compat_css20.h

## Purpose
This header defines the CSS 2.x compatibility contract shared by AtomISP modules: CSS stream state, stream environment, firmware environment, CSS event/buffer wrappers, and statistics buffer types.

## Important APIs and Types
It defines continuous-frame defaults, DVS delay, MIPI buffer fallback sizes, `enum atomisp_css_stream_state`, `struct atomisp_css_isys_config_info`, `struct atomisp_stream_env`, `struct atomisp_css_env`, and wrapper structs for 3A, DIS, CSS buffers, and CSS events. It declares CSS parameter setters, firmware loading, debug helpers, and DVS grid access.

## Control Flow
The header does not implement control flow. Its structures are populated by subdev/ioctl code, consumed by `atomisp_compat_css20.c` to create IA CSS pipes and streams, and later updated by parameter setter APIs before being applied to the running CSS stream or pipe.

## State and Persistence
`atomisp_stream_env` persists inside `atomisp_sub_device` across open, format negotiation, and streaming. Pipe configs and update flags persist until stream stop or CSS reinitialization. Statistics wrapper structs move through driver-owned lists.

## Dependencies and Integration Points
Includes V4L2 media bus and IA CSS headers. It forward-declares AtomISP device/subdevice types and is consumed by file ops, ioctl, subdev, and CSS compatibility code.

## Risks
The structures expose raw IA CSS pointers and fixed arrays indexed by IA CSS enums, so enum drift or out-of-range IDs can corrupt state. Synchronization is external; fields such as stream state and update flags are not self-protecting.

## Test Signals
Compile coverage, stream state transitions, pipe-array indexing, multi-ISYS defaults, ACC stream isolation, and statistics list ownership under stream start/stop validate this interface.
