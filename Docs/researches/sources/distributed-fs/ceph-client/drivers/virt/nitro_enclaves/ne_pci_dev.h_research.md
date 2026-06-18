# sources/distributed-fs/ceph-client/drivers/virt/nitro_enclaves/ne_pci_dev.h

## Purpose
Defines the Nitro Enclaves PCI device ABI, command payloads, reply structure, device state, and exported command helper.

## APIs, Types, and Functions
Important constants include PCI device ID `0xe4c1`, BAR `3`, MMIO offsets `NE_ENABLE`, `NE_VERSION`, `NE_COMMAND`, `NE_EVTCNT`, send/receive buffers, sizes, and MSI-X vectors. It defines `enum ne_pci_dev_cmd_type`, request structs for enclave and slot operations, `struct ne_pci_dev_cmd_reply`, `struct ne_pci_dev`, declaration of `ne_do_request()`, and external `ne_pci_driver`.

## Control Flow and State
No executable flow. The ABI state includes command reply availability, enclave list, event workqueue, MMIO base, PCI mutex, and backing `pci_dev`.

## Dependencies and Integration
Consumed by both `ne_pci_dev.c` and `ne_misc_dev.c`; command structs mirror Nitro Hypervisor expectations and must stay within 240-byte MMIO payload buffers.

## Risks and Test Signals
Risks are ABI drift, padding/size mismatches, endian assumptions, and command sizes exceeding MMIO buffers. Compile-time size checks would be valuable. Tests should validate every request struct size against `NE_SEND_DATA_SIZE` and reply size against `NE_RECV_DATA_SIZE`.
