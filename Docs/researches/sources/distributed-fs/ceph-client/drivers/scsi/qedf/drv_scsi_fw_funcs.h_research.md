# sources/distributed-fs/ceph-client/drivers/scsi/qedf/drv_scsi_fw_funcs.h

## Purpose
`drv_scsi_fw_funcs.h` defines common QEDF SCSI firmware-helper parameter structures and declares helper functions for SGL context initialization.

## Important APIs, types, and functions
`struct scsi_sgl_task_params` describes an SGL pointer, SGL physical address, total buffer size, SGE count, and whether a small middle SGE exists. `struct scsi_dif_task_params` describes DIF/protection settings, including reference/application tags, guard/protection modes, validation/forwarding flags, and connection-error behavior. `struct scsi_initiator_cmd_params` describes extended CDB and sense-data-buffer parameters. The declared functions are `scsi_is_slow_sgl()` and `init_scsi_sgl_context()`.

## Control flow relevance
FCoE firmware helpers use this header to classify SGLs and populate the SGL-related areas of ystorm/mstorm contexts. DIF and initiator command parameter structures are available to higher-level helpers even though this specific C file only uses SGL fields.

## State and persistence behavior
The header has no storage or durable state. It describes caller-owned parameters and firmware-context output fields.

## Dependencies and integration points
It includes QED common HSI, storage common, and FCoE common headers, binding the helper API to QED firmware structures. It is included by both FCoE helper C/H files.

## Risks and test signals
Risks include structure field drift against firmware HSI, unused DIF fields becoming stale, and callers passing inconsistent `num_sges`, `total_buffer_size`, and SGL pointer values. Test signals include compile coverage, static analysis of all call sites, slow-SGL threshold tests, and firmware-context byte comparison for representative SGL layouts.
