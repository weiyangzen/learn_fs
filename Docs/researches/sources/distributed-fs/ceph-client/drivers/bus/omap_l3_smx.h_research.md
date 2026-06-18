# sources/distributed-fs/ceph-client/drivers/bus/omap_l3_smx.h

## Purpose
This header defines the OMAP3 L3 SMX register contract, error status masks, initiator IDs, error code values, runtime state struct, and status-bit-to-agent-offset tables consumed by `omap_l3_smx.c`.

## Important APIs, Types, and Functions
Important constants include `L3_ERROR_LOG`, `L3_ERROR_LOG_ADDR`, sideband status registers, `L3_STATUS_0_TIMEOUT_MASK`, `L3_AGENT_STATUS_CLEAR_IA`, and `L3_AGENT_STATUS_CLEAR_TA`. `enum omap3_l3_initiator_id` and `enum omap3_l3_code` provide semantic decode values. `struct omap3_l3` stores the device pointer, optional clock pointer, L3 base, IRQs, and an `inband` bit. `omap3_l3_app_bases`, `omap3_l3_debug_bases`, and `omap3_l3_bases` map status bits to register-block offsets.

## Control Flow
The header has no active control flow, but its arrays directly drive interrupt routing: the IRQ handler indexes `omap3_l3_bases[int_type][err_source]` to find the agent block whose error log should be read and cleared.

## State and Persistence
The arrays and `shift` constant are static file-scope definitions emitted into each includer. The `struct omap3_l3` definition describes per-device runtime state, while hardware state remains in L3 registers.

## Dependencies and Integration Points
It depends on low-level I/O pointer checking for the local `__raw_readll`/`__raw_writell` macros and is tightly bound to OMAP3 TRM bit assignments. It is private to the OMAP3 SMX driver.

## Risks and Test Signals
The critical risk is stale or incomplete bit-to-offset mapping, especially because reserved entries are zero and can redirect decoding to the base block. The local raw 64-bit MMIO macros may also be architecture-sensitive. Test signals include matching decoded initiator names and addresses against hardware documentation and no false handling of reserved status bits.
