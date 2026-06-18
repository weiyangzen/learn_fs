# sources/distributed-fs/ceph-client/drivers/scsi/mvumi.h

## Purpose

`mvumi.h` defines the firmware ABI, register abstraction, command frame formats, SGL formats, handshake pages, event structures, runtime HBA state, and per-chip operation template for the Marvell UMI SCSI driver. It is the contract between `mvumi.c` and the MV9143/MV9580 firmware message-unit protocol.

## Important APIs, Types, and Definitions

- Driver and PCI constants include `MV_DRIVER_NAME`, version fields, `PCI_DEVICE_ID_MARVELL_MV9143`, `PCI_DEVICE_ID_MARVELL_MV9580`, internal command wait time, inquiry UUID offsets, and `MVUMI_MAX_SG_ENTRY`.
- `struct mvumi_hw_regs` stores mapped MMIO register pointers and bit masks for doorbells, interrupts, resets, and inbound/outbound communication-list control.
- Doorbell and command flag enums define handshake, reset, bus-change, event, data direction, DMA/PIO, and PRDT-in-host bits.
- Event structures include `mvumi_hotplug_event`, `mvumi_driver_event`, `mvumi_event_req`, and `mvumi_events_wq`.
- SGL ABI types are `mvumi_sgl` and `mvumi_compact_sgl`, with macros `sgd_getsz`, `sgd_setsz`, and `sgd_inc` adapting to compact SGL firmware capability.
- `mvumi_cmd`, `mvumi_msg_frame`, and `mvumi_rsp_frame` define command tracking and inbound/outbound wire frames.
- Handshake definitions include firmware states, signatures, status/state encoders, `mvumi_hs_header`, and pages 1 through 4 for firmware capability, host info, firmware control, and communication-list info.
- `struct mvumi_hba` is the central runtime controller state; `struct mvumi_instance_template` provides function pointers for chip-specific command issue, interrupt control, ring checks, status reads, and reset.

## Control Flow and Contracts

The header encodes a strict startup contract. Firmware starts in a handshake state, page 1 reports capabilities and dimensions, the driver allocates communication-list memory sized from those fields, and pages 2 through 4 send host identity and DMA addresses back to firmware. The frame and SGL structures must remain layout-compatible with firmware, including compact SGL stride selection and endian handling by the C file.

Normal command flow uses `mvumi_msg_frame` as the host-to-firmware CDB container and `mvumi_rsp_frame` as the firmware-to-host completion container. Tags are indexes into `hba->tag_cmd`; request IDs optionally protect against stale completions. `mvumi_instance_template` isolates the few hardware differences that cannot be represented just by register offsets.

## State and Persistence Behavior

`struct mvumi_hba` persists for the bound PCI device lifetime. It stores mapped BARs, DMA communication lists, shadow pointers, handshake page, firmware capability results, host limits, ring positions, firmware state, command/tag pools, target bitmap, event lists, and hotplug thread state. The header defines no disk persistence. It does define firmware-visible persistent-like protocol fields such as controller firmware version and target WWID inquiry offsets, but actual persistence is handled by firmware.

## Dependencies and Integration Points

The header assumes Linux kernel list, atomic, mutex, wait queue, PCI, DMA, SCSI, and workqueue types are already available through the C file includes or kernel build context. It directly supports the SCSI midlayer through `mvumi_cmd_priv`, which stores a pointer in each `scsi_cmnd` private area. Firmware event IDs and Marvell-specific SCSI CDB constants integrate the driver with controller management functions such as shutdown cache flush and event retrieval.

## Risks and Edge Cases

- Several structures are firmware ABI layouts but are not all explicitly marked packed; compiler layout assumptions must match the platform ABI expected by firmware.
- `IS_DMA64` is a compile-time `sizeof(dma_addr_t)` check, not a runtime device capability check; the C code still falls back if 64-bit DMA mask setup fails.
- Compact SGL macros cast between normal and compact descriptors and increment a typed pointer through byte arithmetic; misuse can corrupt frame payloads.
- `HSP_MAX_SIZE` uses a GCC statement expression, tying this header to kernel/GNU C expectations.
- `mvumi_hba` mixes fields protected by `host_lock`, device mutexes, atomics, and wait queues; the header does not document lock ownership, so callers must follow `mvumi.c` conventions.

## Test Signals

Header correctness is signaled by successful builds with both supported PCI device IDs, sparse and endian checks around frame/SGL fields, firmware handshake negotiation with and without compact/dynamic-source capabilities, high queue-depth tag-stack tests, event payload parsing, and command-private storage validation through `cmd_size = sizeof(struct mvumi_cmd_priv)`.
