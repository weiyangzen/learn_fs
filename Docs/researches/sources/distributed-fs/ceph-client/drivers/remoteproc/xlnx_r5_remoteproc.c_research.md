# sources/distributed-fs/ceph-client/drivers/remoteproc/xlnx_r5_remoteproc.c

## Purpose

This file implements the Xilinx/ZynqMP, Versal, and Versal Net R5/R52 remoteproc platform driver. It builds remoteproc instances for RPU child cores, configures cluster mode and TCM layout through Xilinx platform-management firmware, maps TCM/SRAM/reserved-memory carveouts, handles IPI mailbox kicks, and supports both normal firmware boot and attach to firmware already running in memory.

## Important APIs, Types, And Functions

Primary data structures are `struct mem_bank_data`, `struct zynqmp_sram_bank`, `struct mbox_info`, `struct rsc_tbl_data`, `struct zynqmp_r5_core`, and `struct zynqmp_r5_cluster`. The cluster stores mode and child core pointers. Each core stores TCM bank descriptors, SRAM banks, PM domain ID, remoteproc handle, optional mailbox information, and loaded resource-table metadata.

The remoteproc operations in `zynqmp_r5_rproc_ops` include prepare/unprepare, start/stop, ELF load and sanity operations, firmware resource-table parsing, mailbox kick, attach/detach, and loaded resource table access. `zynqmp_r5_rproc_start()` uses `zynqmp_pm_request_node()` and `zynqmp_pm_request_wake()` with a boot memory selector derived from the boot address. `zynqmp_r5_rproc_stop()` uses `PM_RELEASE_NODE` when available or falls back to `PM_FORCE_POWERDOWN`.

Memory setup is split across `add_tcm_banks()`, `add_mem_regions_carveout()`, and `add_sram_carveouts()`. TCM information can come from DT `reg` plus power domains via `zynqmp_r5_get_tcm_node_from_dt()`, or from legacy hardcoded ZynqMP TCM tables via `zynqmp_r5_get_tcm_node()`.

Mailbox setup uses `zynqmp_r5_setup_mbox()`, `zynqmp_r5_mb_rx_cb()`, `handle_event_notified()`, and `zynqmp_r5_rproc_kick()`. RX acknowledges the mailbox and schedules work that scans all remoteproc notify IDs.

## Control Flow

`zynqmp_r5_remoteproc_probe()` allocates a cluster, populates child platform devices, sets driver data, initializes cluster/core state, and registers cleanup. `zynqmp_r5_cluster_init()` reads `xlnx,cluster-mode`, accepts split or lockstep mode, determines TCM mode, validates child core count, allocates child device and core arrays, creates remoteproc instances, optionally sets up mailboxes, and initializes hardware mode through platform-management firmware.

`zynqmp_r5_add_rproc_core()` allocates a remoteproc, disables recovery and IOMMU, sets `auto_boot = false`, registers with remoteproc, and then tries to locate a preloaded resource table. If the magic-bearing metadata in the first `memory-region` entry is valid, the rproc state becomes `RPROC_DETACHED`.

Prepare powers on TCM banks and registers carveouts unless already detached, then adds reserved-memory and SRAM carveouts. Start requests and wakes the core from low or high vectors. Stop releases or powers down the PM node. Unprepare releases all TCM power-domain nodes. Shutdown handles kexec by shutting down running rprocs or detaching attached ones.

## State And Persistence

Per-core state persists until cluster cleanup. TCM banks are requested during prepare and released during unprepare. The resource table VA and size persist for detached attach mode after metadata validation. Mailbox channels are manually allocated and freed, not devm-managed. Platform firmware owns durable RPU mode, TCM configuration, wake, node request, and power-down state.

## Dependencies And Integration Points

The driver depends on remoteproc, reserved memory, mailbox framework, Xilinx IPI message formats, Xilinx firmware PM APIs, device tree child nodes, power-domain bindings, and PM domain IDs such as `PD_R5_0_ATCM`. It binds `xlnx,versal-net-r52fss`, `xlnx,versal-r5fss`, and `xlnx,zynqmp-r5fss`.

Important DT inputs include `xlnx,cluster-mode`, `xlnx,tcm-mode`, child `power-domains`, optional child `reg` TCM resources, `memory-region`, optional `sram`, and optional `mboxes`/`mbox-names`.

## Risks And Edge Cases

The source in this tree contains duplicated declarations and duplicated comments, including a duplicate `enum rpu_tcm_comb tcm_mode;`, which is a compile-integrity risk. `zynqmp_r5_get_rsc_table_va()` returns early on invalid magic without unmapping `rsc_data_va`, so the error path appears to leak an ioremap. Mailbox support is optional and failure only warns, so IPC may silently run without kicks if DT is incomplete. Lockstep mode with two enabled child nodes ignores the second node. Hardcoded legacy TCM tables are retained for old ZynqMP DTs and can diverge from actual hardware if bindings are wrong.

The driver disables recovery, so remote firmware faults are not automatically recovered. Resource-table attach depends on the first memory-region containing a packed metadata structure with exact magic and complement values.

## Test Signals

Test signals include probe under split and lockstep DTs, PM firmware calls for RPU and TCM modes, remoteproc boot and stop, TCM/SRAM/reserved-memory carveout registration, IPI kick and RX notification behavior, detached attach with valid and invalid resource-table metadata, and shutdown behavior during kexec. Compile testing should catch the duplicated declaration in this source snapshot.
