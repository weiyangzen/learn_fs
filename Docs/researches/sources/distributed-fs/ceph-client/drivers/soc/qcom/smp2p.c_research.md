# sources/distributed-fs/ceph-client/drivers/soc/qcom/smp2p.c

## Purpose

`smp2p.c` implements Qualcomm Shared Memory Point-to-Point communication. It exposes inbound SMEM bits as nested interrupts and outbound SMEM bits as `qcom_smem_state` providers, using mailbox or syscon IPC kicks to notify the remote processor.

## Important APIs, Types, and Functions

Firmware ABI is `struct smp2p_smem_item`, containing magic, version, features, local/remote pids, entry counts, flags, and up to 16 named 32-bit entries. Driver state uses `struct qcom_smp2p` and per-entry `struct smp2p_entry`. Core functions include `qcom_smp2p_alloc_outbound_item()`, `qcom_smp2p_negotiate()`, `qcom_smp2p_start_in()`, `qcom_smp2p_notify_in()`, `qcom_smp2p_intr()`, irqchip operations, `smp2p_update_bits()`, inbound/outbound entry setup, and `smp2p_parse_ipc()`.

## Control Flow

Probe reads SMEM item ids and local/remote pids, requests a mailbox channel or falls back to `qcom,ipc` syscon, allocates/initializes the outbound SMEM item, parses child nodes into inbound interrupt domains or outbound state entries, scans early inbound entries, kicks the remote, requests a threaded IRQ, and configures wake IRQ support. Incoming IRQs acquire the inbound SMEM item if needed, negotiate protocol version/features, detect SSR restart flags, match newly valid entries, compare current values to `last_value`, and invoke nested IRQs for enabled rising/falling bits. Outbound updates read-modify-write the local entry under a spinlock and kick when changed.

## State and Persistence Behavior

SMEM items persist in shared memory and are single-writer/single-reader by design. The driver resets outbound entries during probe and clears `valid_entries` on remove. Inbound `last_value`, valid-entry count, negotiation state, and SSR ack state are volatile. SSR ack toggles an outbound flag bit to acknowledge remote restarts.

## Dependencies and Integration Points

Dependencies include SMEM allocation/get, SMEM state registry, irqdomain/irqchip, threaded IRQs, mailbox framework, syscon regmap fallback, wake IRQ support, and DT child node contracts. Consumers use standard IRQ phandles for inbound bits and `qcom,smem-states` for outbound bits.

## Risks and Edge Cases

`qcom_smp2p_check_ssr()` resets `last_value` for all inbound entries whenever SSR ack is enabled, even before confirming a restart happened, which can suppress edge detection around restart checks. `qcom_smp2p_outbound_entry()` does not check `out->valid_entries` against `SMP2P_MAX_ENTRY`, so too many outbound child nodes can overflow the entry array. Remove and unwind call `mbox_free_channel()` even when fallback syscon mode set `mbox_chan` to NULL. Protocol negotiation depends on remote version initialization and can stall if remote never writes a version.

## Test Signals

Test mailbox and syscon IPC modes, missing DT properties, outbound item already exists, unsupported inbound version, more than 16 entries, inbound entry late allocation, rising/falling interrupt delivery, irqchip line-level reads before allocation, outbound state updates and kicks, SSR restart/ack flow, wake IRQ setup failure, unwind cleanup, and remove clearing `valid_entries`.
