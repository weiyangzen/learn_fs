# sources/distributed-fs/ceph-client/drivers/media/pci/Kconfig

Purpose: top-level Kconfig menu for PCI/PCIe media adapters. It gates camera, analog TV, hybrid, digital TV, Intel, and sample skeleton PCI media drivers behind `PCI` and `MEDIA_PCI_SUPPORT`.

Important APIs/types/functions: defines `MEDIA_PCI_SUPPORT` menuconfig and `VIDEO_PCI_SKELETON`. It sources many subdriver Kconfig files based on feature groups such as `MEDIA_CAMERA_SUPPORT`, `MEDIA_ANALOG_TV_SUPPORT`, and `MEDIA_DIGITAL_TV_SUPPORT`.

Control flow: configuration enters this file only under `if PCI`. If `MEDIA_PCI_SUPPORT` is enabled, it conditionally exposes driver families by media capability class. The skeleton driver requires `SAMPLES`, `MEDIA_TEST_SUPPORT`, `PCI`, and `VIDEO_DEV`, and selects vb2 DMA-contig support.

State/persistence: kernel configuration symbols only.

Dependencies/integration: integrates PCI media drivers into the global media Kconfig tree and ties each family to media feature-class symbols.

Risks/test signals: misplaced source includes can hide whole driver families. Kconfig tests should cover camera-only, analog-only, digital-only, and mixed support, plus skeleton sample dependencies, with `PCI=n` ensuring the menu is absent.
