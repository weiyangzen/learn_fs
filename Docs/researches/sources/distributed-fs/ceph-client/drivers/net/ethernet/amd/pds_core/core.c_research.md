# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/pds_core/core.c

## Purpose
`core.c` implements core AMD/Pensando device services after PCI BARs are mapped: notification registration, interrupt allocation, queue/completion-queue allocation, device core initialization, VIF-type discovery, setup/teardown, interrupt start/stop, firmware-down/up recovery, PCI reset work, and periodic health handling.

## Important APIs, Types, And Functions
Notifier APIs are `pdsc_register_notify`, `pdsc_unregister_notify`, and `pdsc_notify`. Interrupt APIs are `pdsc_intr_alloc` and `pdsc_intr_free`. Queue APIs are `pdsc_qcq_alloc` and `pdsc_qcq_free`, with helpers `pdsc_q_map`, `pdsc_cq_map`, and QCQ interrupt allocation/free. Device lifecycle APIs are `pdsc_setup`, `pdsc_teardown`, `pdsc_start`, `pdsc_stop`, `pdsc_fw_down`, `pdsc_fw_up`, `pdsc_pci_reset_thread`, and `pdsc_health_thread`.

## Control Flow
`pdsc_setup` calls `pdsc_dev_init` to reset/identify firmware and allocate MSI-X vectors, then `pdsc_core_init` to allocate AdminQ and NotifyQ QCQs, submit `PDS_CORE_CMD_INIT`, read hardware queue indices/types, and map the kernel doorbell page. On initial setup it also allocates VIF-type status from defaults and firmware identity, and publishes debugfs VIF information. Successful setup sets `adminq_refcnt` to one and clears firmware-dead state.

QCQ allocation creates per-descriptor software info arrays with completions, allocates coherent queue and completion memory aligned to `PDS_PAGE_SIZE`, optionally places notify queue and completion queue in one contiguous coherent allocation, binds interrupts for interrupt-backed queues, maps descriptor pointers, and creates debugfs nodes. Free removes debugfs, frees IRQ, coherent memory, and software arrays.

Firmware health recovery is state-driven. `pdsc_health_thread` holds `config_lock`, skips transition states, calls `pdsc_is_fw_good`, and if running state changed invokes `pdsc_fw_down` or `pdsc_fw_up`. Firmware-down sets `PDSC_S_FW_DEAD`, waits for AdminQ users to drain, reports devlink health, notifies clients of reset state 0, masks interrupts, and tears down core queues without removing VIF metadata. Firmware-up rebuilds setup without initial-only allocation, restarts interrupts, increments recovery count, marks devlink reporter healthy, and notifies clients of reset state 1.

## State And Persistence
Runtime state lives in `struct pdsc`: state bits, firmware status/generation/heartbeat, workqueue work items, health reporter pointer, interrupt table, AdminQ/NotifyQ QCQs, doorbell mapping, VIF-type status, and last notify event ID. The blocking notifier chain is static module state. No persistent storage is written; recovery reconstructs queues and MMIO mappings from firmware identity and PCI BAR state.

## Dependencies And Integration Points
The file depends on PCI MSI-X APIs, DMA coherent allocation, vmalloc/vcalloc, devlink health reporter updates, workqueues, timers indirectly through `main.c`, debugfs helpers, AdminQ ISR from `adminq.c`, device command helpers from `dev.c`, and firmware ABI definitions from `linux/pds/*`. Auxiliary clients observe reset/link events through the notifier chain.

## Risks
Queue setup is sensitive to alignment, descriptor sizing, ring power-of-two lengths, CQ color handling, and firmware-returned queue IDs. `pdsc_adminq_wait_and_dec_once_unused` busy-waits until AdminQ users drain; a leaked reference can stall recovery. `pdsc_fw_down` returns early for VFs after setting firmware-dead state, so VF recovery semantics depend on PF reset handling. PCI health work deliberately queues reset work to avoid reset/health deadlock; changes in locking order around `config_lock` and PCI reset callbacks can reintroduce deadlocks.

## Test Signals
Exercise PF initial setup, MSI-X allocation failures, AdminQ/NotifyQ QCQ allocation failures, firmware-down/up recovery, devlink health reports, notifier events to clients, PCI bad-status reset work, teardown during active AdminQ commands, and debugfs queue visibility.
