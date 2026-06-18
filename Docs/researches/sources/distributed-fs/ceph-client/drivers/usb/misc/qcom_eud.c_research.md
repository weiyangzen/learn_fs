# sources/distributed-fs/ceph-client/drivers/usb/misc/qcom_eud.c

Purpose: Qualcomm Embedded USB Debug platform driver. It exposes sysfs control to enable EUD, programs secure mode-manager registers, handles EUD interrupts, and drives a USB role switch between host/device based on attach status.

Important APIs and types: `struct eud_chip`, `enable_eud()`, `disable_eud()`, sysfs `enable`, `usb_attach_detach()`, `pet_eud()`, hard IRQ/threaded IRQ handlers, `eud_probe()`, and `eud_remove()`. It depends on MMIO, `qcom_scm_io_writel()`, `usb_role_switch`, IRQ wake, and OF compatible `qcom,eud`.

Control flow: probe gets the USB role switch, maps EUD registers, records a second memory resource as the SCM mode-manager physical base, requests a threaded IRQ, enables wake, and exposes sysfs. Writing `1` to `enable` writes secure enable, sets EUD enable/int masks, and switches USB role to device. IRQ top half reads status: VBUS changes schedule the thread, safe-mode interrupts call `pet_eud()`. The thread switches USB role to device or host and clears the VBUS interrupt latch.

State and persistence: `enabled` and `usb_attached` are in-memory flags; hardware registers and role switch state persist until disabled or platform reset. Risks include `enable_store()` not clearing `chip->enabled` on disable, no locking around sysfs/IRQ state, secure monitor failures requiring rollback, and wakeup state setup without a matching `device_init_wakeup(true)`. Test signals include sysfs enable/disable, SCM write failures, role-switch failure logs, VBUS and safe-mode IRQs, wake IRQ behavior, and remove while enabled.
