
# sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/pci.c

Purpose: PCI frontend for Intel Trace Hub controllers. It matches Intel NPK PCI IDs, enables the PCI device, maps BAR resources, allocates IRQ vectors, selects hardware quirks, and delegates subdevice creation to `intel_th_alloc()`.

Important APIs/types/functions: `intel_th_pci_probe()` and `intel_th_pci_remove()` are the `pci_driver` callbacks. `intel_th_pci_activate()`/`deactivate()` manipulate PCI config register `NPKDSC_TSACT` for TSCU-capable devices. Static `intel_th_drvdata` instances describe `multi_is_broken` and 2.x capabilities. `intel_th_pci_id_table[]` maps many Intel device IDs to quirk data.

Control flow: probe enables and claims PCI regions, maps config and STH software BARs, optionally records the RTIT BAR, allocates up to eight IRQ vectors, builds an Intel TH resource array, calls `intel_th_alloc()`, installs parent activate/deactivate hooks, and sets bus mastering. Remove frees the Intel TH core tree and IRQ vectors.

State and persistence: stores `struct intel_th` as PCI drvdata. Quirk selection is static from device ID. No persistent storage.

Dependencies and integration: depends on PCI managed resource APIs, MSI/MSI-X/INTx vector allocation, Intel TH core allocation, and `pci_ids.h`.

Risks: resource array order must match `enum th_mmio_idx`; wrong BAR assumptions break subdevice windows. IRQ vector allocation failure is tolerated only if negative path is considered; vector resource numbering must stay aligned with MSU expectations. Activate and deactivate both set `NPKDSC_TSACT`, which should be verified against hardware semantics.

Test signals: probe on IDs with and without RTIT BARs, no-IRQ systems, TSCU-capable and 1.x quirk devices, runtime trace activation, remove/unload, and `lspci`/sysfs device topology checks.
