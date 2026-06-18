# sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc.h

## Purpose
`lpfc.h` is the central private header for the Broadcom/Emulex lpfc Fibre Channel driver. It defines driver-wide limits, feature flags, Fibre Channel and HBA state enums, DMA and queue buffer types, vport and HBA state containers, congestion-management structures, VMID metadata, RAS/debug support, and SLI revision abstraction helpers.

## Important APIs, types, and functions
- Global limits cover targets, discovery concurrency, queue depth, S/G segment counts, NVMe segment counts, IOCB pool size, link speeds, MSI-X vectors, mailbox wait modes, heartbeat/error polling intervals, and vport naming.
- DMA/buffer types include `struct lpfc_dmabuf`, `struct lpfc_nvmet_ctxbuf`, `struct lpfc_dma_pool`, `struct hbq_dmabuf`, and `struct rqb_dmabuf`.
- `lpfc_vpd_t` stores vital product data, firmware revisions, names, and SLI3 feature bits with endian-specific bitfields.
- `struct lpfc_stats` tracks ELS, frame, link, FCP, and error counters.
- VMID structures include `struct lpfc_vmid`, `union lpfc_vmid_io_tag`, `struct lpfc_vmid_context`, and priority range/info structures.
- State enums include `enum discovery_state`, `enum hba_state`, `enum lpfc_hba_flag`, `enum lpfc_fc_flag`, `enum lpfc_load_flag`, interrupt modes, RAS states, mailbox buffer states, and HBA bit flags.
- Congestion management types include `struct lpfc_cgn_param`, `struct lpfc_cgn_ts`, `struct lpfc_cgn_info`, `struct lpfc_cgn_stat`, `struct lpfc_cgn_acqe_stat`, `struct rx_info_entry`, and `struct lpfc_rx_info_monitor`.
- `struct lpfc_vport` represents a physical or NPIV/Fabric vport with FC identity, discovery lists/counters, RSCN state, timers, tunables, VMID table, debugfs entries, receive buffers, FDMI masks, and NVMe local port state.
- `struct lpfc_hba` is the main adapter object. It contains function pointers for SCSI buffer handling, IOCB/WQE issue/prep, mailbox issue, slow-ring processing, board/link operations, block-guard prep, SLI4 and SLI state, workqueues/timers, PCI/MMIO mappings, mailbox/HBQ resources, VPD strings, SCSI/IOCB pools, RRQ state, DMA/mempools, port/vport allocation, fabric scheduler state, debugfs/error-injection state, heartbeat/RAS/CMF/congestion/FPIN state, CPU hotplug/polling hooks, and debug log storage.
- Inline helpers include `lpfc_shost_from_vport`, `lpfc_set_loopback_flag`, `lpfc_is_link_up`, `lpfc_worker_wake_up`, `lpfc_readl`, `lpfc_sli_read_hs`, `lpfc_phba_elsring`, CPU selection helpers, `lpfc_sli4_mod_hba_eq_delay`, `DECLARE_ENUM2STR_LOOKUP`, `lpfc_is_vmid_enabled`, and SLI2/3 vs SLI4 job accessors such as `get_job_ulpstatus`, `get_job_word4`, `get_job_cmnd`, `get_job_ulpcontext`, `get_job_rcvoxid`, `get_job_data_placed`, `get_job_abtsiotag`, and `get_job_els_rsp64_did`.

## Control flow and state
The header itself has little control flow, but its data model drives the driver. `struct lpfc_hba` owns adapter-level queues, memory pools, MMIO mappings, worker state, timers, SLI revision dispatch, PCI identity, feature configuration, congestion state, and port list. `struct lpfc_vport` owns per-NPort discovery and protocol state and points back to its HBA. Function pointers inside `lpfc_hba` abstract SLI generation differences and allow common code to call revision-specific implementations.

Inline helpers encode common control decisions: link-up state is true for `LPFC_LINK_UP`, `LPFC_CLEAR_LA`, or `LPFC_HBA_READY`; worker wake-up sets `LPFC_DATA_READY` and wakes `work_waitq`; MMIO reads returning `0xffffffff` are treated as `-EIO`; `lpfc_sli_read_hs` snapshots host status/work status and clears error attention; `lpfc_phba_elsring` returns the correct ELS ring for SLI2/3 or SLI4; job accessors select IOCB fields for SLI2/3 or WQE/WCQE fields for SLI4.

## State and persistence behavior
Most state is volatile driver runtime state in `lpfc_hba` and `lpfc_vport`: discovery state, FC IDs, flags, lists, timers, queues, DMA pools, mempools, config parameters, congestion counters, VMID tables, debug traces, and MMIO pointers. Some fields mirror persistent or firmware-provided information, including VPD, firmware names/revisions, flash congestion parameters (`LPFC_CFG_PARAM_MAGIC_NUM`, `LPFC_PORT_CFG_NAME`), serial/model strings, WWNN/WWPN, and RAS/congestion buffers registered with firmware. The header defines structures for these persisted/firmware interfaces but does not itself perform I/O.

## Dependencies and integration points
`lpfc.h` integrates with the SCSI host model, PCI/MMIO, DMA pools, mempools, timers, workqueues, debugfs, Fibre Channel transport, NVMe-FC/NVMET, CPU hotplug, firmware mailbox/SLI definitions from other lpfc headers, and kernel congestion/FPIN concepts. The Makefile builds many C files that include this header and fill in the function-pointer implementations.

## Risks and edge cases
- `struct lpfc_hba` is very broad; changes can affect SCSI, NVMe, discovery, interrupt handling, mailbox, firmware logging, congestion management, and vports at once.
- Endian-specific VPD bitfields must match firmware layout on both big- and little-endian builds.
- MMIO helper `lpfc_readl` treats all-ones as device error; callers must propagate `-EIO` to avoid using invalid register snapshots.
- SLI revision helpers must be kept aligned with IOCB/WQE layout changes; wrong field selection can corrupt completions or aborts.
- Many counters and lists are protected by different locks (`hbalock`, `port_list_lock`, VMID lock, debug/RAS locks, SCSI buffer locks). Locking rules must be preserved outside this header.
- Conditional debugfs and NVMe feature macros change struct contents and defaults, so ABI assumptions inside the driver must be configuration-aware.

## Test signals
- Build with SLI3/SLI4, debugfs on/off, NVMe-FC enabled/disabled, and big-endian bitfield coverage where available.
- Link-state and worker wake-up paths should update flags and wake waiters as expected.
- Simulated MMIO all-ones reads should force `-EIO` and error-attention handling should snapshot/clear registers.
- SLI4 and SLI3 completion accessor unit tests or trace validation should return equivalent semantic fields.
- VMID, CMF/congestion, RAS logging, and vport discovery tests should verify counters, timers, and config bounds.
