## sources/distributed-fs/ceph-client/drivers/fpga/altera-cvp.c

Purpose: this is an FPGA manager driver for Intel/Altera Configuration via Protocol over PCIe. It programs full RBF bitstreams through the device's PCI Vendor Specific Extended Capability and, when available, BAR0 memory writes.

Important APIs and functions: `struct altera_cvp_conf` stores the PCI device, mapped BAR, VSEC offset, selected write method, manager name, packet counters, and version-specific operations. `struct cvp_priv` distinguishes V1 and V2 behavior: V1 uses dummy writes and 4-byte blocks, while V2 uses a credit register and 4 KiB blocks. FPGA manager callbacks are `altera_cvp_state()`, `altera_cvp_write_init()`, `altera_cvp_write()`, and `altera_cvp_write_complete()`. The driver also exposes a driver sysfs attribute `chkcfg` to enable optional configuration-error checks.

Control flow: probe finds the Altera VSEC ID, verifies CvP enablement, enables PCI memory space directly through the command register, requests BAR0, selects BAR MMIO writes or config-space writes as a fallback, selects V1/V2 private ops, and registers an FPGA manager. Programming rejects partial reconfiguration, derives `numclks` from compressed/encrypted flags, switches clock and mode bits, clears stale state, sets `CVP_CONFIG`, waits for `CFG_RDY`, starts transfer, streams blocks while respecting credits, tears down control bits, checks latched errors, clears CvP mode, and waits for user mode.

State and persistence: runtime state includes global `altera_cvp_chkcfg`, per-device sent packet count, `numclks`, VSEC offset, BAR mapping, and selected write path. Hardware state is held in VSEC status/control/error registers and may survive failed programming until teardown or `clear_state()` runs.

Dependencies and integration: it integrates with PCI core, the FPGA manager framework, PCI config-space VSEC accessors, optional BAR IO mapping, and module init/exit for both PCI driver registration and driver sysfs attribute lifetime.

Risks: the PCI ID table matches any Altera vendor device, so VSEC validation is critical. Directly enabling/disabling PCI memory space bypasses `pci_enable_device()` to handle unassigned large BARs, but removal clears the memory bit even if it was enabled before probe. Buffer casts to `u32 *` assume data alignment tolerated by architecture. V2 credit accounting stores `sent_packets` in `u32` but compares with an 8-bit credit value, relying on wrap behavior. Optional error checking is global across all devices.

Test signals: test VSEC-missing and CvP-disabled probe failures, BAR mapping fallback to config-space writes, V1 and V2 devices, compressed/encrypted clock ratio flags, large images crossing multiple credit windows, latched error paths, usermode timeout, and `chkcfg` sysfs toggling during programming.
