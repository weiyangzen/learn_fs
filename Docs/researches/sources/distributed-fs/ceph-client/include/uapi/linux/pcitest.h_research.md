# sources/distributed-fs/ceph-client/include/uapi/linux/pcitest.h

Purpose: Defines ioctl ABI for the PCI endpoint test driver.

Important APIs/types/functions: Exports `PCITEST_BAR`, `PCITEST_INTX_IRQ`, `PCITEST_MSI`, `PCITEST_WRITE`, `PCITEST_READ`, `PCITEST_COPY`, `PCITEST_MSIX`, IRQ type set/get, BAR query/subrange, doorbell, clear IRQ, IRQ type constants, `PCITEST_FLAGS_USE_DMA`, and `struct pci_endpoint_test_xfer_param`.

Control flow: Userspace opens the endpoint test device, selects IRQ mode, triggers BAR tests, runs read/write/copy transfers with a size or transfer parameter, triggers interrupts or doorbells, and checks test results returned by the driver.

State and persistence behavior: The header defines transient test commands. Runtime state includes selected IRQ type, endpoint BAR mappings, DMA use flag, and transfer buffers; it does not persist beyond the device/test session.

Dependencies and integration points: Integrates with PCI endpoint controller/function testing, kernel PCI endpoint test driver, and hardware validation suites.

Risks: Transfer sizes and DMA flags must be validated to avoid overrun or mapping misuse. IRQ mode transitions need cleanup. The older unsigned-long size ioctls may have compat width concerns.

Test signals: Run endpoint test utility across INTx/MSI/MSI-X, BAR and BAR subrange checks, DMA and non-DMA transfers, read/write/copy sizes including zero and large values, doorbell signaling, and clear IRQ behavior.
