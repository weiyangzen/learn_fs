# sources/distributed-fs/ceph-client/arch/sh/drivers/pci/common.c



Source read size: 160 lines, 3926 bytes.



Purpose: shared SH PCI helper code for early config access, 66 MHz capability probing, error timers, and PCI status error handling.

Important APIs/types/functions: `early_read/write_config_{byte,word,dword}()`, `pci_is_66mhz_capable()`, `pcibios_enable_timers()`, `pcibios_handle_status_errors()`, and fake `pci_dev`/`pci_bus` construction.

Control flow: early helpers synthesize a minimal bus/device around a `pci_channel` before enumeration; capability probing scans bus device functions; error handlers report and clear PCI status bits and temporarily disable noisy IRQs via timers.

State and persistence: static fake objects are reused only during early calls; per-controller error timers and IRQ numbers persist in `pci_channel`.

Dependencies and integration points: used by SH7751/SH7780 setup and generic `pcibios_report_status`; depends on Linux PCI config accessors, timers, and interrupt APIs.

Risks and test signals: fake static objects are not reentrant; error IRQ backoff must re-enable reliably. Test early config reads before bus scan, 66 MHz-capable devices, parity/master/target abort injection, and timer re-enable.
