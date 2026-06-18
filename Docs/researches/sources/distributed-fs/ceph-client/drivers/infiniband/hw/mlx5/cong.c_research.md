# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/cong.c

## Purpose
This file creates a debugfs interface for querying and modifying mlx5 RoCE congestion-control parameters. It exposes RP, NP, and general RRoCE ECN fields as per-port files when firmware permits congestion query and modification.

## Important APIs, types, and functions
Public lifecycle functions are `mlx5_ib_init_cong_debugfs` and `mlx5_ib_cleanup_cong_debugfs`. Internal mapping helpers include `mlx5_ib_param_to_node`, `mlx5_get_cc_param_val`, and `mlx5_ib_set_cc_param_mask_val`. Firmware command helpers are `mlx5_ib_get_cc_params` and `mlx5_ib_set_cc_params`, backed by `mlx5_cmd_query_cong_params` and `MLX5_CMD_OP_MODIFY_CONG_PARAMS`. Debugfs operations are `set_param`, `get_param`, and `dbg_cc_fops`.

## Control flow
Initialization checks the global mlx5 debugfs root, obtains the native port mdev, validates `cc_query_allowed` and `cc_modify_allowed`, allocates `mlx5_ib_dbg_cc_params`, creates a `cc_params` directory under the mlx5 device debugfs root, and creates one 0600 file per supported parameter. General RTT response DSCP fields are skipped unless RoCE and general RoCE congestion-control capabilities are present.

Reads allocate a query output mailbox, select the RP/NP/general congestion node from the parameter offset, execute a query command, extract the field, and copy a decimal value to userspace. Writes copy a short numeric string from userspace, parse a `u32`, allocate a modify input mailbox, set opcode and protocol, set the target field and field-select mask, and execute the firmware modify command.

Cleanup removes the debugfs subtree recursively, frees the parameter container, and nulls the pointer.

## State and persistence behavior
The debugfs files are runtime-only. Values read and written are firmware congestion parameters for the native port mdev. The driver stores only debugfs dentries and small parameter descriptors; no disk persistence is provided.

## Dependencies and integration points
This code depends on debugfs, mlx5 command mailbox layouts, native-port lookup for multiport/LAG setups, firmware congestion capabilities, and `cmd.c` query support.

## Risks
Risks include exposing powerful tuning knobs through debugfs, wrong field-select masks for NP/general fields, port number off-by-one handling, stale native-port devices during teardown, partial debugfs creation, and accepting syntactically valid but semantically out-of-range values without driver-side validation.

## Test signals
Test capability-gated creation, read/write of every RP/NP/general parameter on supported firmware, absence of RTT DSCP files when capabilities are missing, cleanup after partial allocation failure, invalid user input lengths and nonnumeric writes, multiport native-port routing, and verification that firmware values change as expected.
