# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/cmd.h

## Purpose
`cmd.h` defines the mlxsw firmware command mailbox interface. It provides mailbox allocation helpers, command execution wrappers, opcode/status names, and packed field accessors for firmware, board info, asynchronous queue capabilities, firmware-area mapping, resource queries, switch profile configuration, register access, DQ/CQ/EQ ownership transitions, and queue context programming.

## Important APIs, Types, and Functions
The central API is `mlxsw_cmd_exec()`, wrapped by `mlxsw_cmd_exec_in()`, `mlxsw_cmd_exec_out()`, and `mlxsw_cmd_exec_none()`. Command-specific wrappers include `mlxsw_cmd_query_fw()`, `mlxsw_cmd_boardinfo()`, `mlxsw_cmd_query_aq_cap()`, `mlxsw_cmd_map_fa()`, `mlxsw_cmd_unmap_fa()`, `mlxsw_cmd_query_resources()`, `mlxsw_cmd_config_profile_set()`, `mlxsw_cmd_access_reg()`, SDQ/RDQ `sw2hw`, `hw2sw`, `2err`, query helpers, and CQ/EQ ownership/query helpers. `MLXSW_ITEM*` macros define mailbox fields.

## Control Flow and State
Callers allocate a 4096-byte mailbox, populate fields through generated accessors, and invoke wrappers with opcode, opcode modifier, input modifier, direct-output flag, reset allowance, and mailbox sizes. Firmware commands mutate hardware state: mapping/unmapping firmware pages, configuring switch profiles, transitioning descriptor/completion/event queues between software and hardware ownership, moving queues to error state, and accessing registers. Query commands return firmware revision, board PSID/VSD, AQ capabilities, resources, and queue contexts.

There is no local persistent software state beyond temporary mailboxes, but command results drive core initialization, bus setup, devlink resources, queue allocation, and Spectrum profile selection. The header also encodes firmware ABI details such as resource query limits, VPM entry limits, boardinfo string lengths, flood/LAG/CQE timestamp modes, and CQE versions.

## Dependencies and Integration Points
The file depends on `item.h` generated field helpers, kernel allocation, and `struct mlxsw_core` command transport implemented elsewhere. It is used by mlxsw core, PCI/I2C bus code, queue setup, firmware bootstrap, resource discovery, and Spectrum profile configuration.

## Risks and Test Signals
Risks include opcode/status mismatch, mailbox field offset/width drift, incorrect wrapper opcodes, resource query loop limits, profile fields set without corresponding capability bits, queue state transition misuse, and the `__mlxsw_cmd_query_dq()` wrapper using the `2ERR_DQ` opcode despite comments describing `QUERY_DQ`, which deserves scrutiny against firmware expectations. Test signals are mlxsw probe and firmware bootstrap, PSID read, firmware-area mapping, resource table discovery until end ID, Spectrum profile set, SDQ/RDQ/CQ/EQ create/destroy/query, reset-time access-reg paths, and negative tests for firmware status-to-string reporting.
