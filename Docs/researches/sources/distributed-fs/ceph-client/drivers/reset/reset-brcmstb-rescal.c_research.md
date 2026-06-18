# sources/distributed-fs/ceph-client/drivers/reset/reset-brcmstb-rescal.c

Purpose: Broadcom RESCAL reset provider for SATA/PCIe recalibration blocks.

Important APIs/types/functions: `struct brcm_rescal_reset`, `brcm_rescal_reset_set()`, `brcm_rescal_reset_xlate()`, and `brcm_rescal_reset_probe()`.

Control flow: probe maps resource 0 and registers a single reset. `.reset` sets the start bit, verifies it latched, polls the status bit with `readl_poll_timeout()`, then clears start. Custom xlate returns ID 0 for zero-cell reset consumers.

State and persistence: no cached state; calibration completion is read from hardware status.

Dependencies and integration: platform driver for `brcm,bcm7216-pcie-sata-rescal`, MMIO, polling helpers, reset framework.

Risks and test signals: timeout and failed start paths are the main runtime failures. Test zero-cell phandle translation, status timeout logging, and successful SATA/PCIe bring-up.
