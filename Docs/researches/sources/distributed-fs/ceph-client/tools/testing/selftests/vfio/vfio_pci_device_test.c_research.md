# sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/vfio_pci_device_test.c

## Purpose

`vfio_pci_device_test.c` is a kselftest harness for basic VFIO PCI device access. It opens a user-selected PCI BDF through the local `libvfio` selftest helpers, verifies config-space access, BAR mmap discovery, MSI/MSI-X eventfd wiring, and optional device reset support.

## Important APIs, Types, and Functions

The file uses `FIXTURE()` and `TEST_F()` from `kselftest_harness.h`. `struct iommu`, `struct vfio_pci_device`, and `struct vfio_pci_bar` come from `libvfio.h`. Important helper calls are `vfio_selftests_get_bdf()`, `iommu_init()`, `vfio_pci_device_init()`, `vfio_pci_device_cleanup()`, `vfio_pci_device_match()`, `vfio_pci_config_readw()`, `vfio_pci_config_writew()`, `vfio_pci_irq_enable()`, `vfio_pci_irq_trigger()`, `vfio_pci_irq_disable()`, and `vfio_pci_device_reset()`. The local `read_pci_id_from_sysfs()` macro reads `vendor` and `device` from `/sys/bus/pci/devices/<bdf>/`.

## Control Flow

The main fixture initializes an IOMMU container/group and opens the VFIO PCI device for each test. `config_space_read_write` compares VFIO config space against sysfs vendor/device IDs, toggles `PCI_COMMAND_MASTER`, and confirms the write takes effect. `validate_bars` walks the six standard BARs and checks that mmap-capable regions were automatically mapped by `vfio_pci_device_init()`. A second parameterized fixture runs the same IRQ test for MSI and MSI-X: it limits vector count to `MAX_TEST_MSI`, enables vectors, verifies each eventfd is empty, triggers the vector through VFIO, reads the eventfd value, then disables IRQs. `reset` skips devices without `VFIO_DEVICE_FLAGS_RESET` and calls reset otherwise.

## State and Persistence Behavior

No repository or filesystem state is persisted beyond temporary VFIO file descriptors and sysfs reads. The tests intentionally mutate device state: they toggle PCI bus mastering, enable/disable MSI or MSI-X vectors, and may reset the device. Fixture teardown closes VFIO state and IOMMU mappings.

## Dependencies and Integration Points

The test requires a VFIO-bound PCI device passed by BDF, suitable IOMMU support, `/dev/vfio` access, sysfs PCI attributes, Linux VFIO UAPI definitions, and the selftests `libvfio` helper library. It integrates with the kselftest harness for reporting and skip behavior.

## Risks and Edge Cases

The config-space test assumes bus mastering is initially disabled and that toggling it is safe for the selected device. The IRQ test only validates software trigger/eventfd behavior, not real device-generated interrupts. `ASSERT_GT(open(...), 0)` treats fd 0 as failure even though it is technically valid. Hardware reset and bus-master changes can disturb a device that is not dedicated to testing.

## Test Signals

Expected pass signals are matching sysfs/VFIO IDs, successful bus-master bit transitions, non-null mmap pointers for mmap-capable BARs, `EAGAIN` on empty nonblocking eventfds, eventfd value `1` after each trigger, and a successful reset or skip when reset is unsupported.
