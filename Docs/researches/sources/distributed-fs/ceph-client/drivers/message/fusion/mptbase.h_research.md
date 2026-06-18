# sources/distributed-fs/ceph-client/drivers/message/fusion/mptbase.h

## Purpose
`mptbase.h` is the shared contract for the legacy LSI Fusion MPT driver family. It defines versioning, adapter limits, message-frame layouts, scatter-gather flag helpers, target/device bookkeeping, IOC management status bits, event structures, protocol-driver callback types, and the large `MPT_ADAPTER` object consumed by the SCSI, Fibre Channel, SAS, LAN, and ioctl drivers.

## Important APIs, Types, and Functions
Core public types include `MPT_ADAPTER`, `MPT_FRAME_HDR`, `MPT_FRAME_TRACKER`, `MPT_MGMT`, `CONFIGPARMS`, `MPT_SCSI_HOST`, `VirtTarget`, `VirtDevice`, `MPT_IOCTL_EVENTS`, `mptfc_rport_info`, and bus/config structs for SPI, SAS, RAID, and FC. Public callback contracts are `MPT_CALLBACK`, `MPT_EVHANDLER`, and `MPT_RESETHANDLER`; reset phases are `MPT_IOC_SETUP_RESET`, `MPT_IOC_PRE_RESET`, and `MPT_IOC_POST_RESET`. Important exported base entry points include `mpt_attach()`, `mpt_detach()`, `mpt_register()`, `mpt_deregister()`, event/reset registration, message-frame get/put/free helpers, `mpt_send_handshake_request()`, `mpt_verify_adapter()`, `mpt_config()`, firmware-memory helpers, RAID page helpers, task-management flag helpers, and reset handlers.

## Control Flow
Protocol modules register callbacks with the base driver and receive a callback index that is embedded into message contexts. They allocate frames with `mpt_get_msg_frame()`, fill MPI request structures, post via `mpt_put_msg_frame()` or `mpt_put_msg_frame_hi_pri()`, and receive completions through the registered callback. The base header also standardizes config-page access through `CONFIGPARMS`, reset fan-out through reset handlers, and adapter discovery through `ioc_list` plus `mpt_verify_adapter()`.

## State and Persistence
Almost all persistent runtime state is anchored in `MPT_ADAPTER`: PCI resources, MMIO register mappings, request/reply frame DMA pools, chain buffers, sense buffers, IOC facts, port facts, cached firmware, per-protocol callback indices, event logs, SCSI host pointers, FC rport lists and workqueues, SAS topology/discovery state, management command completions, reset/task-management flags, and counters for resets/timeouts. State is in-memory and tied to PCI device lifetime; there is no disk persistence.

## Dependencies and Integration Points
The header depends on kernel PCI, mutex, procfs, SCSI, netdev-visible declarations through consumers, and the LSI MPI headers under `lsi/`. It is included by `mptbase.c`, `mptctl.c`, `mptfc.c`, `mptlan.c`, and other Fusion protocol drivers. Its callback and frame-context conventions are the integration point between Linux subsystems and firmware message passing.

## Risks and Edge Cases
`MPT_ADAPTER` is very broad and shared across many protocol drivers, so layout or semantic changes have high blast radius. Message context encodes callback and frame index, making corruption or stale contexts dangerous. Several pointer casts and `CAST_U32_TO_PTR` helpers expose compat-width risks. DMA frame, chain, and sense-buffer sizing depends on IOC facts and compile-time SGE limits. Bitfield-like status macros and shared management command state require careful reset-path synchronization.

## Test Signals
Useful signals include building all Fusion protocol modules, PCI probe/remove smoke tests, request/reply stress with callback index validation, fault injection for frame allocation and config-page reads, reset fan-out tests covering all three reset phases, DMA mapping tests for 32-bit and 64-bit SGE paths, and SCSI/FC/LAN functional traffic after IOC reset.
