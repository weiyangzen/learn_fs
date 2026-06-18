# sources/distributed-fs/ceph-client/drivers/infiniband/hw/efa/efa_admin_defs.h

## Purpose

`efa_admin_defs.h` defines EFA admin, async event, and event queue descriptor formats shared by admin command code and hardware queues. It covers common AQ/ACQ descriptors, control-buffer descriptors, AENQ entries, EQ completion events, completion statuses, and masks for phase/opcode/event fields.

## Important APIs, Types, and Definitions

- `enum efa_admin_aq_completion_status`: firmware completion status codes and their semantic categories.
- Admin queue descriptors: `efa_admin_aq_common_desc`, `efa_admin_ctrl_buff_info`, `efa_admin_aq_entry`, `efa_admin_acq_common_desc`, and `efa_admin_acq_entry`.
- Async events: `efa_admin_aenq_common_desc` and `efa_admin_aenq_entry`.
- Event queues: `efa_admin_eqe_event_type`, `efa_admin_comp_event`, and `efa_admin_eqe`.
- Masks: command ID, phase, control data, control data indirect, AENQ phase, EQE phase, and EQE event type.

## Control Flow

The header has no executable code. `efa_com.c` uses phase bits in ACQ/AENQ/EQE descriptors to decide which entries hardware has produced, uses command IDs to match completions to outstanding contexts, and uses control-buffer descriptors for commands that require payloads larger than inline AQ space.

## State and Persistence Behavior

Descriptor fields live in coherent DMA rings shared with the device. Producer/consumer counters and phase bits in `efa_com` structures interpret these descriptors. Control buffer descriptors may point directly to DMA payloads or to indirect page-list chunks, so they are part of command lifetime and DMA mapping state.

## Dependencies and Integration Points

It depends on `efa_common_mem_addr` from common definitions and Linux bit macros. It is included by `efa_com.h` and command definition headers. Hardware, firmware, `efa_com_cmd_exec`, AENQ interrupt handling, and EQ interrupt handling all rely on these layouts.

## Risks and Edge Cases

- Phase-bit handling requires DMA read barriers before reading the rest of an entry; consumers must not bypass the pattern used in `efa_com.c`.
- Command IDs are only 12 bits, with low bits used for completion-context indexing; queue depth must remain compatible with that encoding.
- Control-buffer indirect chaining has no helper in this header, so wrapper code must validate lengths and DMA addresses carefully.
- Unknown completion statuses collapse to generic `-EINVAL` in `efa_com.c`, potentially hiding firmware-specific diagnostics unless extended status is logged elsewhere.

## Test Signals

Tests should validate descriptor sizes, phase wrap behavior, command ID masking, direct and indirect control-buffer commands, AENQ/EQE parsing, and status-to-errno mapping in the communication layer.
