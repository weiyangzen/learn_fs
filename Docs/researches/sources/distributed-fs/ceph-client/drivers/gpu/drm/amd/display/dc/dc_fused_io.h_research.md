# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_fused_io.h

## Purpose
`dc_fused_io.h` declares public fused IO helpers that execute atomic write-poll-read sequences over I2C or AUX for a `dc_link`.

## Important APIs
`dm_atomic_write_poll_read_i2c` accepts write, poll, and read `mod_hdcp_atomic_op_i2c` structures plus poll timeout and MSB mask. `dm_atomic_write_poll_read_aux` mirrors the same contract for AUX operations. Both return `bool` success and write read data into the mutable read operation structure.

## Control Flow And State
The header has no logic. The API contract implies callers allocate and retain operation buffers for the duration of the call, and the implementation sends the sequence to DMUB as a fused command.

## Dependencies And Integration Points
It includes `dc.h` and `mod_hdcp.h`, tying it to DC link objects and HDCP operation formats. HDCP authentication and DMUB IO execution are the main integration points.

## Risks
The API does not encode maximum buffer size, nullability of write/poll/read operations, or whether read data comes from I2C/AUX response semantics. Callers must provide a fully initialized link and DDC path.

## Test Signals
Compile coverage for HDCP users, static checks on nullability assumptions, and fake-DMUB tests for both exported functions are the expected signals.
