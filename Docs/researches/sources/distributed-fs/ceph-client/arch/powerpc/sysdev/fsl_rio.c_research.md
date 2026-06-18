<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_rio.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_rio.c

Purpose: Freescale MPC85xx/MPC86xx Serial RapidIO master-port support, including local/maintenance config access, inbound memory windows, machine-check recovery, port error clearing, RMU doorbell/port-write/message integration, and mport registration.

Important APIs/types/functions: platform setup `fsl_rio_setup()` and `fsl_of_rio_rpn_probe()`, config ops `fsl_local_config_read/write()` and `fsl_rio_config_read/write()`, inbound mapping ops `fsl_map_inb_mem()` and `fsl_unmap_inb_mem()`, `fsl_rio_port_error_handler()`, optional exported `fsl_rio_mcheck_exception()`, global `rio_regs_win`, `rmu_regs_win`, `rio_law_start`, `dbell`, and `pw`.

Control flow: probe maps SRIO and RMU registers, allocates `rio_ops`, locates message/doorbell/port-write nodes, allocates doorbell and port-write state, then iterates child port nodes. For each port it reads `cell-index` and LAW range, allocates and initializes a `rio_mport` plus private data, reserves the IO resource, checks/restarts port training if needed, reports link width/status, configures host/master flags, sets ATMU pointers, accepts all destination IDs, programs the maintenance window, maps it, initializes RMU and inbound ATMUs, stores mport pointers in doorbell/port-write structures, and registers the mport. Config reads/writes serialize access to a single maintenance ATMU window and validate offset/length alignment; reads use exception-table protected loads. Inbound mapping validates power-of-two size, alignment, overlap, and free ATMU availability before programming translation registers.

State and persistence: global SRIO/RMU MMIO windows, LAW start, doorbell and port-write singleton state, per-mport resources, `rio_priv` register/window pointers, and hardware ATMU/port status registers persist while the driver is active.

Dependencies and integration points: depends on RapidIO core, OF nodes/properties for SRIO/RMU/message/doorbell/port-write units, DMA/resource APIs, exception tables for fault-tolerant maintenance reads, FSL RMU helper functions declared in `fsl_rio.h`, and optional PPC_E500 machine-check path.

Risks: single global RMU/doorbell/port-write state assumes one SRIO complex. Maintenance window access is serialized globally because the ATMU target is reprogrammed per transaction. Error cleanup frees only some partially registered per-port resources. Inbound overlap checks use hardware window fields and must match size encoding. Port restart is heuristic and may fail on bad links.

Test signals: SRIO mport registration, config read/write to local and remote devices, maintenance read fault recovery, doorbell and port-write interrupts, inbound memory map/unmap validation, link restart logs, and RapidIO enumeration over active ports validate this driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_rio.c -->
