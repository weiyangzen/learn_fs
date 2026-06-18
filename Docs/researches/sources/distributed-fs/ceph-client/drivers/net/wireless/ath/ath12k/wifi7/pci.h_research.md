# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/pci.h

## Purpose

`pci.h` is the public header for Wi-Fi 7 ath12k PCI driver registration.

## Important APIs

It declares `int ath12k_wifi7_pci_init(void);` and `void ath12k_wifi7_pci_exit(void);`. These functions register and unregister the Wi-Fi 7 PCI driver with the shared ath12k PCI layer.

## Control Flow And Integration

The Wi-Fi 7 module core includes this header and calls `ath12k_wifi7_pci_init()` during module initialization and `ath12k_wifi7_pci_exit()` during module exit. The implementations live in `pci.c` and wrap `ath12k_pci_register_driver()` / `ath12k_pci_unregister_driver()` for `ATH12K_DEVICE_FAMILY_WIFI7`.

## State And Persistence Behavior

The header owns no state. The declared init/exit functions mutate global PCI driver registration state in the kernel.

## Dependencies

No external structures are needed by the prototypes. Include guards prevent duplicate declarations.

## Risks And Edge Cases

The init function can fail if shared PCI registration fails; callers must preserve module init error handling and call exit only when registration succeeded. Header/API drift would break the Wi-Fi 7 core module.

## Test Signals

Build coverage should ensure declarations match `pci.c`. Module load/unload should register and unregister the PCI family exactly once, and PCI devices should bind only after successful init.
