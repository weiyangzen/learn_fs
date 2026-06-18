<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ssb/pcihost_wrapper.c -->
# sources/distributed-fs/ceph-client/drivers/ssb/pcihost_wrapper.c

Purpose: wraps a PCI device that exposes a Sonics Silicon Backplane into an `ssb_bus`, so SSB core drivers can bind below an ordinary `pci_driver`.

Important APIs/types/functions: `ssb_pcihost_register()` is the exported entry point. It installs `ssb_pcihost_probe()` and `ssb_pcihost_remove()` into the caller's `struct pci_driver`, optionally attaches `ssb_pcihost_pm_ops`, then calls `pci_register_driver()`. Probe allocates `struct ssb_bus`, enables the PCI function, requests BAR regions, sets bus mastering, disables the Broadcom retry timeout register field, and calls `ssb_bus_pcibus_register()`. Suspend/resume call `ssb_bus_suspend()`/`ssb_bus_resume()` around PCI save/disable/sleep and restore/enable sequencing.

Control flow: PCI matching enters probe, SSB enumeration and child-device registration happen in the SSB core, and remove unwinds in reverse order through `ssb_bus_unregister()`, region release, device disable, and `kfree()`.

State and persistence: state is runtime only: the allocated `ssb_bus` is stored as PCI driver data and freed on removal. PCI config state is saved across sleep but no durable data is written.

Dependencies and integration: depends on PCI core, PM sleep, and the SSB PCI bus registration path. The caller supplies IDs/name while this wrapper supplies common host behavior.

Risks: failure unwinds must stay paired with each probe step. PM resume re-enables PCI before SSB resume; failures can leave children unavailable. The retry-timeout config write is device-specific and should be limited to hardware where it is valid.

Test signals: bind/unbind a Broadcom SSB PCI device, confirm child cores enumerate, suspend/resume with wake-capable child devices, and inject failures for enable, region request, and SSB registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ssb/pcihost_wrapper.c -->
