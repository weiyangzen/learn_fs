# sources/distributed-fs/ceph-client/include/linux/i3c/ccc.h

## Purpose
Defines I3C Common Command Code identifiers and payload structures used by master controllers to configure and query I3C devices.

## APIs, Control Flow, and State
`I3C_CCC_ID()` builds broadcast/direct command IDs. Macros enumerate broadcast, unicast, dual-mode, vendor, event, status, HDR, and XTIME command IDs. Payload structs cover event enable/disable, max write/read length, DEFSLVS device descriptors, test mode, dynamic address assignment, PID/BCR/DCR/status reads, master handoff, bridged targets, max data speed, HDR capability, SETXTIME/GETXTIME, and generic command destinations. `struct i3c_ccc_cmd` binds direction, command ID, destination payloads, destination count, and returned `enum i3c_error_code`. State is transient command/payload buffers; payload data must be DMA-able.

## Dependencies, Integration, Risks, and Tests
Depends on bitops and `i3c/device.h` for error codes and device concepts. Integrates with I3C master controller command paths, dynamic address assignment, multi-master support, IBI control, HDR capability negotiation, and vendor extensions. Risks include using broadcast commands with multiple destinations incorrectly, endian mistakes in packed payloads, non-DMA-able payload buffers, mismatched payload length, and subcommand typos such as the comment spelling `ddefined`. Test signals include CCC command encoding tests, ENTDAA/SETDASA/SETNEWDA flows, GETPID/BCR/DCR parsing, HDR capability negotiation, and controller error-code propagation.
