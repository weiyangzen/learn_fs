# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/amd5536udc_pci.c

Purpose: PCI bus glue for the AMD5536 UDC, mapping hardware resources and invoking the shared UDC core.

Important APIs, types, and functions: global `udc` enforces a single controller instance. `udc_pci_probe` enables the PCI device, requests BAR0 memory, maps registers, requests IRQ, initializes register/FIFO pointers in `struct udc`, sets bus mastering/MWI, initializes DMA pools when enabled, and calls `udc_probe`. `udc_pci_remove` unregisters the gadget UDC, frees DMA pools, resets the controller, releases IRQ/mapping/memory/PCI state, and calls `udc_remove`. `pci_id` matches AMD vendor device `0x2096` with USB device class.

Control flow: PCI probe performs allocation and hardware resource acquisition in stages with labeled unwind. If core probe succeeds, the global `udc` pointer is set. Remove deletes the gadget UDC before requiring no gadget driver to remain, then performs hardware and memory teardown.

State and persistence: all runtime state is in one allocated `struct udc` and the global pointer. PCI driver data points to the device object. No durable state exists.

Dependencies and integration points: depends on PCI, MMIO, IRQ, DMA pools, and the AMD5536 core declarations from `amd5536udc.h`. It registers through `module_pci_driver`, exposing a UDC to the gadget framework after `udc_probe`.

Risks: the file assumes one UDC only. Remove uses global `udc->gadget` rather than local `dev->gadget`, which is safe only if the singleton invariant holds. Resource unwind must mirror acquisition. DMA mode can be disabled through module parameters when alignment-sensitive gadget functions fail.

Test signals: probe on matching PCI hardware, verify BAR mapping and IRQ handling, bind a gadget, enumerate and transfer data, unload with and without a gadget bound, test probe failure injection at each resource stage, and run both `use_dma=1` and `use_dma=0`.
