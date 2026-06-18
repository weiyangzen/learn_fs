# sources/distributed-fs/ceph-client/drivers/virt/coco/pkvm-guest/arm-pkvm-guest.c

## Purpose
Initializes hypervisor services for arm64 pKVM protected guests: memory share/unshare operations and optional MMIO guard registration.

## APIs, Types, and Functions
Public entry is `pkvm_init_hyp_services()`. Key helpers are `arm_smccc_do_one_page()`, `__set_memory_range()`, `pkvm_set_memory_encrypted()`, `pkvm_set_memory_decrypted()`, and `mmio_guard_ioremap_hook()`. It registers `arm64_mem_crypt_ops`.

## Control Flow and State
Initialization checks that required KVM hypervisor service IDs exist, queries the pKVM granule size, rejects impossible granules larger than a page, stores `pkvm_granule`, and registers memory encryption ops. Memory transitions iterate each page and each pKVM granule with SMCCC calls. The MMIO guard hook filters device mappings, rounds to page boundaries, and asks the hypervisor to guard every page.

## Dependencies and Integration
Depends on Arm SMCCC, arm64 hypervisor service discovery, `arm64_mem_crypt_ops_register()`, and `arm64_ioremap_prot_hook_register()`.

## Risks and Test Signals
Risks are partial memory-range transitions, ignored MMIO guard failures beyond WARN, and assumptions about granule dividing a page. Tests should cover service absence, bad granule return, memory share/unshare failure, MMIO mappings with device and non-device pgprot values, and DMA interactions.
