# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/aie2_message.c

## Purpose
This file is the AIE2 firmware mailbox marshalling layer. It sends management messages, creates and destroys firmware contexts and mailbox channels, queries metadata/telemetry/status, configures CUs and debug buffers, and converts userspace command buffers into firmware execute messages.

## Important APIs, Types, And Functions
Management APIs include `aie2_suspend_fw()`, `aie2_resume_fw()`, runtime config get/set, PASID assignment, metadata/version queries, context create/destroy, host-buffer mapping, status/telemetry queries, async-event registration, and app-health query. Execution APIs include `aie2_execbuf()`, `aie2_cmdlist_multi_execbuf()`, `aie2_cmdlist_single_execbuf()`, `aie2_sync_bo()`, and `aie2_config_debug_bo()`. `aie2_msg_init()` selects legacy or NPU command-list operation tables based on firmware feature bits.

## Control Flow
Synchronous management commands use `aie2_send_mgmt_msg_wait()`, which tears down the management channel on timeout and maps non-success firmware status to `-EINVAL`. Context creation sends `CREATE_CONTEXT`, builds x2i/i2x mailbox resource descriptors from firmware queue addresses, maps an MSI-X vector, starts a mailbox channel, and rolls back by destroying the firmware context on failure. Command execution either sends a direct CU/DPU request or fills a reusable device command buffer with one or more command-list slots, flushes it for device access, builds a chain request, and sends it asynchronously through the context channel.

## State, Dependencies, Integration, Risks, And Tests
State touched here includes management/context mailbox channels, firmware context IDs, hardware context counts, selected exec message ops, command-list BO contents, and temporary DMA buffers used for queries. Dependencies include mailbox helpers, PCI IRQ mapping, GEM lookup/vmap/device addresses, DMA/IOMMU message allocation, DRM cache flushing, userspace copy, bitfield packing, and protocol structs from `aie2_msg_priv.h`. Risks include command payload size validation, leaked GEM references or vmaps on early returns, firmware protocol drift, noncoherent DMA synchronization, channel teardown during concurrent use, and inconsistent legacy versus NPU command formats. Test signals include protocol version/metadata queries, context create rollback failures, CU config validation, multi-command chain error indices, NPU preempt/ELF feature gating, telemetry/status buffer sizing, app health on timeout, and management timeout recovery.
