# sources/distributed-fs/ceph-client/drivers/block/mtip32xx/mtip32xx.c

## Purpose
This file implements the Micron RealSSD/P320/P420 PCIe block driver. It binds Micron PCI IDs, initializes an AHCI-like controller/port, exposes disks named `rssd*`, translates blk-mq requests into ATA NCQ FIS command tables, handles internal ATA ioctls, and manages controller reset, interrupt, timeout, rebuild, suspend/resume, shutdown, sysfs, and debugfs behavior.

## Important APIs, Types, And Functions
The central runtime state is `struct driver_data` and `struct mtip_port` from `mtip32xx.h`, with per-request `struct mtip_cmd` allocated as the blk-mq PDU. PCI lifecycle is owned by `mtip_pci_probe()`, `mtip_pci_remove()`, `mtip_pci_suspend()`, `mtip_pci_resume()`, and `mtip_pci_shutdown()`. Module lifecycle registers a dynamic block major and the PCI driver in `mtip_init()` and tears them down in `mtip_exit()`.

Hardware setup flows through `mtip_hw_init()`, `mtip_detect_product()`, `hba_setup()`, `mtip_dma_alloc()`, `mtip_init_port()`, and `mtip_start_port()`. Normal I/O enters through `mtip_queue_rq()`, maps scatter-gather lists in `mtip_hw_submit_io()`, fills `host_to_dev_fis` and AHCI command headers, and starts hardware with `mtip_issue_ncq_command()`. Reserved/internal commands use `mtip_exec_internal_command()` and `mtip_issue_reserved_cmd()`. Completion is split across `mtip_irq_handler()`, `mtip_handle_irq()`, `mtip_workq_sdbfx()`, `mtip_complete_command()`, and blk-mq `.complete` callback `mtip_softirq_done_fn()`.

Error and maintenance paths include `mtip_cmd_timeout()`, `mtip_service_thread()`, `mtip_handle_tfe()`, `mtip_restart_port()`, `mtip_device_reset()`, `mtip_quiesce_io()`, `mtip_ftl_rebuild_poll()`, `mtip_check_surprise_removal()`, and state-gating helpers `is_se_active()` and `is_stopped()`. User-visible support includes `mtip_block_ioctl()`, `mtip_block_compat_ioctl()`, `mtip_hw_ioctl()`, ATA pass-through helpers, `mtip_block_getgeo()`, sysfs `status`, and debugfs `rssd/<disk>/{flags,registers}`.

## Control Flow
At load, `mtip_init()` registers a block major and PCI driver. Probe chooses a NUMA node, allocates `driver_data`, enables PCI/MSI/DMA, builds an ISR workqueue and CPU bindings, applies PCI quirks, then calls `mtip_block_initialize()`. Block initialization brings up hardware, allocates a blk-mq tag set with one reserved internal-command tag, allocates a gendisk, assigns an `rssd*` name via an IDA, reads IDENTIFY/log/SMART state, sets capacity, adds the disk, and starts the service thread. If an FTL rebuild marker is present, disk addition is delayed while the service thread polls until rebuild completion.

For I/O, blk-mq calls `mtip_queue_rq()`. Passthrough/reserved requests become non-NCQ internal commands. Normal reads/writes are rejected if secure erase, removal, over-temperature, write-protect, or rebuild-failed flags block them. Otherwise the request is started, DMA-mapped, encoded as `ATA_CMD_FPDMA_READ` or `ATA_CMD_FPDMA_WRITE`, and issued by setting SActive and Command Issue bits for the request tag. If internal command or error handling flags are active, the tag is parked in `port->cmds_to_issue` and later issued by the service thread.

Interrupts read HBA/port status, acknowledge port status, queue per-slot-group completion work for SDB FIS completions, process legacy internal-command completions, and wake the service thread for taskfile/interface errors. Completion workers clear hardware completed registers and complete each request. blk-mq completion unmaps DMA, releases unaligned-command budget, and ends the request. Timeouts set `MTIP_PF_TO_ACTIVE_BIT`, wake the service thread, reset the device, requeue parked commands, or fail requests if reset fails.

## State And Persistence Behavior
Persistent media lives on the SSD; the driver stores only volatile kernel state. Important state bits live in `dd->dd_flag` and `port->flags`: remove-pending, secure-lock, over-temperature, write-protect, rebuild-failed, init-done, internal-command active, error-handling active, timeout active, issue-commands, rebuild, and service-thread stop. DMA-coherent buffers hold RX FIS, IDENTIFY data, SMART data, log data, command list entries, and per-command tables. `rssd_index_ida` persists naming only for the lifetime of the module. Debugfs and sysfs report live state but do not persist configuration.

## Dependencies And Integration Points
The driver integrates with PCI/MSI, DMA mapping/coherent allocation, blk-mq, gendisk/block-device operations, ATA command definitions, AHCI register definitions, debugfs, sysfs device attributes, NUMA CPU masks, kthreads, workqueues, IRQ affinity, IDA allocation, and compat ioctl translation. It exposes legacy ATA HDIO ioctls and block geometry for userspace tools.

## Risks
This is hardware-facing code with several race-sensitive paths: surprise removal while registers are being read, interrupt completion workers racing with teardown, internal commands pausing normal NCQ, timeout recovery resetting active hardware, and unaligned write depth accounting. ATA pass-through ioctls copy user buffers and map DMA buffers, so size checks and cleanup order matter. The service-thread wait condition relies on flag bits rather than a separate queue. `mtip_exit()` unregisters the block major before the PCI driver, which is unusual and should be checked against kernel teardown expectations. FTL rebuild polling can block device availability for a long period.

## Test Signals
Useful signals include successful module load with version log, PCI probe for supported IDs, `rssd*` disk creation with correct capacity, sysfs `status` transitions, debugfs flags/register reads, read/write fio or blktests runs, ATA ioctl paths (`HDIO_GET_IDENTITY`, SMART, taskfile), timeout injection via blk fake timeout, remove/surprise-remove behavior, suspend/resume/shutdown with standby immediate, FTL rebuild simulation, and teardown under active I/O.
