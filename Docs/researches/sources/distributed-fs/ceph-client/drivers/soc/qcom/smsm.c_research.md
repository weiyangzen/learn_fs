# sources/distributed-fs/ceph-client/drivers/soc/qcom/smsm.c

## Purpose

`smsm.c` implements Qualcomm's Shared Memory State Machine. It exposes local shared-memory state bits through the `qcom_smem_state` provider API and converts remote shared-memory state changes into nested Linux IRQs. The mechanism is SMEM-backed: one region stores per-host state words, another stores an entry/host subscription matrix, and an optional third region reports dynamic host/entry counts.

## Important APIs, Types, and Functions

Core state is held in `struct qcom_smsm`, with per-state-word context in `struct smsm_entry` and outgoing interrupt transport in `struct smsm_host`. `smsm_update_bits()` is the exported state-provider operation. `smsm_intr()` is the threaded parent interrupt handler. `smsm_mask_irq()`, `smsm_unmask_irq()`, `smsm_set_irq_type()`, `smsm_get_irqchip_state()`, and `smsm_irq_map()` implement the child `irq_chip`/domain. Probe helpers parse mailbox channels, legacy `qcom,ipc-N` syscon triples, inbound interrupt-controller children, and optional SMEM size info.

## Control Flow

Probe reads size metadata or falls back to eight entries and three hosts, allocates host/entry arrays, identifies the child node containing `#qcom,smem-state-cells`, parses `qcom,local-host`, resolves each outgoing host transport, allocates or gets SMEM state and interrupt-mask regions, registers the local state provider, and creates IRQ domains for child nodes marked `interrupt-controller`.

State updates take a spinlock, modify the local word, issue a write memory barrier, then notify only hosts whose subscription word intersects the changed bits. Inbound interrupts read the remote state, diff it against `last_value`, and dispatch nested IRQs for enabled rising/falling bit transitions.

## State and Persistence Behavior

Persistent state is shared with remote processors in SMEM. The driver owns volatile Linux objects: IRQ domains, cached `last_value`, enabled/rising/falling bitmaps, mailbox handles, and pointers into SMEM. Masking and unmasking update the SMEM subscription matrix, so remote processors observe local interrupt interest. Remove tears down IRQ domains, mailboxes, and the `qcom_smem_state` registration, but it does not erase shared state words.

## Dependencies and Integration Points

The driver depends on Qualcomm SMEM, `qcom_smem_state`, mailbox, legacy syscon IPC, irqdomain, threaded interrupts, device tree child-node bindings, and platform-driver probing. Consumers reference the state provider through DT, while remote processors signal inbound changes through parent IRQs.

## Risks and Edge Cases

`qcom,local-host` is read without a visible error check or clamp, so malformed DT can point outside allocated host/entry dimensions. Incoming child `reg` values are checked, but the local-host-derived SMEM pointers are not. The state/subscription memory layout assumes firmware and all processors agree on host/entry counts. `smsm_update_bits()` notifies all hosts including possibly local host if subscribed. Incoming callbacks only support edge semantics; non-edge IRQ type requests fail. Shared-memory read/write ordering relies on `wmb()` before kicks and may need platform validation against remote firmware expectations.

## Test Signals

Build-test with mailbox and legacy IPC bindings enabled. DT tests should cover absent size info, custom size info, invalid `reg`, invalid local host, mailbox fallback to syscon, and child interrupt domains. Runtime tests should toggle state bits, verify remote kicks only for subscribed bits, verify nested IRQ delivery for rising and falling edges, verify mask/unmask writes subscription entries, and exercise removal after child IRQ setup.
