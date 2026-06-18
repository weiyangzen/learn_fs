# sources/distributed-fs/ceph-client/tools/testing/selftests/pci_endpoint/pci_endpoint_test.c

Purpose: kselftest harness for the PCI endpoint test driver exposed at `/dev/pci-endpoint-test.0`. It validates BAR accessibility, IRQ modes, data transfer paths, and doorbell support.

Important APIs/types/functions: `pci_ep_ioctl(cmd, arg)` normalizes `ioctl()` results to negative errno. Fixtures `pci_ep_bar`, `pci_ep_basic`, `pci_ep_data_transfer`, and `pcie_ep_doorbell` open/close the device. Variants cover BAR0-BAR5 and memcpy vs DMA data-transfer modes. It uses `struct pci_endpoint_test_xfer_param` and `PCITEST_*` ioctl commands from `pcitest.h`.

Control flow: BAR tests run `PCITEST_BAR` and `PCITEST_BAR_SUBRANGE`, skipping disabled/reserved/unsupported BARs and resource-short cases. Basic tests run consecutive BAR, legacy IRQ, MSI vectors 1..32, and MSI-X vectors 1..2048 after setting and confirming IRQ type. Transfer tests set AUTO IRQ and run read/write/copy across sizes 1, 1024, 1025, 1024000, and 1024001 with and without DMA. Doorbell test sets AUTO IRQ and skips unsupported doorbell.

State and persistence: opens a character device and changes endpoint IRQ mode through ioctls. No files are persisted.

Dependencies/integration: requires endpoint hardware or virtual setup, loaded endpoint test drivers, `/dev/pci-endpoint-test.0`, and the matching UAPI header.

Risks: hardware capabilities vary widely, so skips are expected. MSI-X loop is large and may be slow. Tests assume a single fixed test device name and can fail on systems exposing a different instance.

Test signals: kselftest harness `ASSERT`, `EXPECT`, and `SKIP` lines identify unsupported BARs/features, ioctl setup failures, or data/IRQ failures.
