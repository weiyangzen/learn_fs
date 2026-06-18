# sources/distributed-fs/ceph-client/drivers/media/usb/as102/as10x_cmd.h

## Purpose
Defines the AS10x firmware control protocol ABI: procedure IDs, command header, packed request/response unions, command aggregate, and function prototypes.

## Important APIs, types, and functions
`enum control_proc` maps each command to request and response procedure IDs. `struct as10x_cmd_header_t` contains request id, service program id, version, and data length. Packed unions describe turn on/off, tune, tune status, TPS, PID filter, stream start/stop, demod stats, impulse response, firmware context, register access, config mode changes, memory dump, log dump, and raw data. `struct as10x_cmd_t` combines the header and all possible bodies. Prototypes cover core, stream, and context commands.

## Control flow and state
This header has no runtime flow but defines the memory layout that every command function writes into shared bus token storage. `HEADER_SIZE` drives USB transfer lengths in the command files.

## Dependencies and integration points
Includes `as102_fe_types.h` for tune/status/stat/register data structures. Integrated by AS102 driver, USB token storage, command implementations, and frontend glue.

## Risks and test signals
Because these structs are packed wire ABI, field ordering, type widths, and endian annotations are high-risk. Generic parser expectations also depend on response unions sharing `proc_id` and `error` at the same offsets. Test signals are compile-time packed sizes, command success on hardware, and sparse/endian warnings staying clean when protocol fields are touched.
