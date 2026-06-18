# sources/distributed-fs/ceph-client/include/linux/firmware/imx/sm.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/firmware/imx/sm.h` declares NXP i.MX SCMI extension helpers for miscellaneous controls, CPU control, and logical machine management. The source was read as a complete 99-line file for this report.

## Important APIs, Types, and Functions

It defines SCMI control IDs for i.MX95/i.MX94 audio/wake controls and `SCMI_IMX952_CTRL_BYPASS_AUDMIX`. APIs include `scmi_imx_misc_ctrl_get/set`, `scmi_imx_cpu_start`, `scmi_imx_cpu_started`, `scmi_imx_cpu_reset_vector_set`, `enum scmi_imx_lmm_op`, LMM operation flags, `scmi_imx_lmm_operation`, `scmi_imx_lmm_info`, and `scmi_imx_lmm_reset_vector_set`. Disabled driver configs return `-EOPNOTSUPP`.

## Control Flow

Clients call SCMI extension helpers to query/set SoC controls, start/stop CPUs, program CPU reset vectors, boot/power/shutdown logical machine managers, query LMM info, and set LMM reset vectors.

## State and Persistence Behavior

The header owns no state. Runtime and persistent effects are mediated by SCMI firmware and platform power/control domains.

## Dependencies and Integration Points

It depends on bitfield, errno, SCMI i.MX protocol definitions, and types. It integrates with SCMI transport, NXP SoC control drivers, CPU hotplug/boot flows, and virtualization/partition management.

## Risks and Edge Cases

SCMI IDs are firmware ABI. Disabled helpers fail at runtime; clients must degrade cleanly. Reset-vector programming carries boot/security risk if arguments are wrong.

## Test Signals

SCMI protocol mock tests, CPU start/reset-vector tests, LMM operation tests, unsupported-driver tests, and firmware error-path tests.
