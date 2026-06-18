# sources/distributed-fs/ceph-client/drivers/cxl/pci.c

Purpose: PCI-facing CXL memory-device driver. It binds Type-3 CXL.mem PCI class devices, maps register blocks, initializes the mailbox, discovers capacity/commands/features/PMUs/events, creates the CXL memdev, and handles PCI error/reset and CPER event forwarding.

Important APIs/types/functions: `cxl_pci_probe()`, `__cxl_pci_mbox_send_cmd()`, `cxl_pci_setup_mailbox()`, event IRQ setup helpers, `cxl_event_thread()`, `cxl_pci_mbox_irq()`, `cxl_mbox_sanitize_work()`, RCD link sysfs attributes, PCI error handlers, and `cxl_handle_cper_event()`.

Control flow and state: probe enables PCI, creates `cxl_memdev_state`, maps memdev and component registers, initializes and sizes the mailbox, waits for media/mailbox readiness, enumerates commands, sets timestamp, initializes poison and DPA partitions, sets up features/firmware/sanitize notifiers/FWCTL, adds PMU instances, configures event interrupts if native OS control exists, and saves PCI state. Mailbox access is serialized by `mbox_mutex`, polls the doorbell, supports background commands, treats sanitize as asynchronous delayed-work polling, and uses irq wakeups where available.

Dependencies and integration: integrates PCI, CXL register mapping, CXL mailbox/core, feature/fwctl/fw-upload, CXL PMU, poison/event/EDAC consumers, AER/PCI error handlers, CPER kfifo work, host-bridge `_OSC` native CXL error control, and RCD sysfs.

Risks and test signals: mailbox timeouts, oversized payloads, return-code translation, background command synchronization, sanitize monopolization, event ownership with firmware, reset behavior after SBR, missing component registers, and PMU loop error handling are primary risks. Test kexec stale doorbell, tiny mailbox, no IRQ vectors, firmware-owned event logs, CPER delivery, AER slot reset, RCD attributes, and devices lacking DVSEC/component/PMU blocks.
