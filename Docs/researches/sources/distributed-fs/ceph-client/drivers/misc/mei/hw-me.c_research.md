<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/hw-me.c -->
# sources/distributed-fs/ceph-client/drivers/misc/mei/hw-me.c

Purpose: implements the `mei_hw_ops` backend for classic Intel ME/GSC-style MEI hardware using host and ME circular buffers, PCI firmware-status registers, H_CSR/ME_CSR handshakes, interrupts or polling, and runtime power management.

Important APIs and functions: exported functions are `mei_me_irq_quick_handler()`, `mei_me_irq_thread_handler()`, `mei_me_polling_thread()`, `mei_me_get_cfg()`, `mei_me_dev_init()`, `mei_me_pg_enter_sync()`, and `mei_me_pg_exit_sync()`. Local functions implement MMIO access, FW/TRC status reads, hardware config, interrupt enable/disable/clear, reset/start, host-buffer slot accounting, write/read slots, legacy PGI, D0i3 entry/exit, GSC PXP detection, quirk probes for NM/SPS/IGN firmware, platform `mei_cfg` instances, and the `mei_me_hw_ops` table.

Control flow: initialization allocates a `mei_device` plus `mei_me_hw`, installs common core state via `mei_device_init()`, copies DMA sizes from the selected platform config, and records kind/FW-version support. `mei_start()` calls `hw_config`, `hw_reset`, and `hw_start` through ops. Reset manipulates `H_RST`, `H_IG`, `H_RDY`, interrupt bits, and D0i3 state; start waits for firmware ready, checks GSC PXP mode, releases reset, and marks host ready. The quick IRQ handler disables device interrupts and wakes the thread. The thread clears interrupt status, reacts to firmware reset/not-ready, handles PG/D0i3 interrupts, wakes start waiters, processes inbound slots through `mei_irq_read_handler()`, writes pending queued messages through `mei_irq_write_handler()`, completes callbacks, and re-enables interrupts.

State and persistence: hardware state is in registers; driver state is volatile in `struct mei_me_hw`: config pointer, MMIO base, IRQ, PG/D0i3 state, buffer depth, FW-status reader, polling thread, and activity waitqueue. `struct mei_device` carries reset counters, PG events, PXP mode, HBM state, queues, and DMA descriptors.

Dependencies and integration: depends on `hw-me-regs.h`, `mei_dev.h`, `hbm.h`, tracepoints, PCI config access, kthreads, runtime PM, wait queues, and IRQ infrastructure. It is selected by PCI/platform probe code outside this subset and consumed through the generic MEI core ops wrappers in `mei_dev.h`.

Risks: register bit semantics are delicate. Write-one-to-clear interrupt bits require masking through `mei_hcsr_set()`. H_RST already set before reset needs clearing or reset can be ignored. D0i3 and legacy PGI use multiple wait states and can deadlock or time out if interrupts are lost. The interrupt thread schedules reset on unexpected firmware-not-ready or bad read results, so false positives can cause reset loops. Platform quirk probes read function 0 PCI config and must align with SKU definitions.

Test signals: boot/probe on multiple generations, interrupt and polling modes, reset storm limit behavior, sysfs `fw_status`/`trc`, runtime PM suspend/resume, GSC PXP boot path, DMA-ring negotiation on configured platforms, ftrace `mei_reg_read/write` and `mei_pci_cfg_read`, and fault injection for HBM read errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/hw-me.c -->
