# sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdnsp-pci.c

Purpose: PCI glue for Cadence CDNSP USBSSP hardware. The complete 248-line file was read. It pairs host/device and OTG/DRD PCI functions, maps BAR resources, wires IRQ/resource data into the shared Cadence core, applies a PCI-specific APB timeout override, and registers PM hooks.

Important APIs/types/functions: `cdnsp_get_second_fun()`, `cdnsp_pci_probe()`, `cdnsp_pci_remove()`, `cdnsp_pci_suspend()`, `cdnsp_pci_resume()`, `cdnsp_pci_pm_ops`, `cdnsp_pci_ids`, and `cdnsp_pci_driver`; BAR/function constants and `CHICKEN_APB_TIMEOUT_VALUE`.

Control flow: probe validates function number and paired function, rejects xHCI class ownership, enables PCI, allocates or reuses shared `struct cdns`, maps device BAR2 and records xHCI resources for function 0, records OTG resource/IRQ for function 1, sets APB timeout override, and when both functions are ready calls `cdns_init()` with `cdnsp_gadget_init`.

State and persistence: persistent runtime state is the shared `struct cdns` stored as PCI drvdata and containing mapped registers, xHCI/OTG resources, IRQs, wake state, override timeout, and gadget initializer.

Dependencies/integration: Linux PCI, platform resources, PM, module APIs, `core.h`, and `gadget-export.h`. Integrates enumeration with `cdns_init/remove/suspend/resume` and the CDNSP gadget role.

Risks: shared-object ownership depends on paired function probe/remove order; BAR layout assumptions are fixed; class/function validation can reject unusual firmware enumeration; cleanup must avoid freeing while the sibling function still uses the object.

Test signals: both probe orders, missing sibling function, xHCI-class rejection, BAR request/map failures, `cdns_init()` unwind, remove order permutations, suspend/resume lock behavior, wake-capable runtime PM, and APB timeout propagation into gadget setup.
