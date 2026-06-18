# sources/distributed-fs/ceph-client/arch/x86/mm/mem_encrypt.c

## Purpose
This file contains common x86 memory-encryption setup shared by AMD SME/SEV and Intel TDX paths. It adjusts DMA policy, SWIOTLB sizing, virtio restricted-memory behavior, and boot-time feature reporting.

## Important APIs, Types, and Functions
- `force_dma_unencrypted()` implements `ARCH_HAS_FORCE_DMA_UNENCRYPTED` policy for encrypted guests and host SME devices that cannot address the encryption bit.
- `mem_encrypt_init()` updates SWIOTLB memory attributes, prepares SNP secure TSC state, and prints active encryption features.
- `mem_encrypt_setup_arch()` performs early architecture setup, including SNP e820 fixups and encrypted-guest SWIOTLB sizing.
- `print_mem_encrypt_feature_info()` formats active Intel TDX, AMD SME, SEV, SEV-ES, and SEV-SNP state.

## Control Flow and State
DMA policy is queried per device: encrypted guests always require shared/unencrypted DMA; SME hosts compare device DMA masks against the encryption mask. Architecture setup fixes SNP e820 tables for hosts, then encrypted guests size SWIOTLB to roughly 6 percent of RAM clamped between the default and 1 GiB, and install the virtio restricted-memory callback. Runtime initialization exits unless memory encryption is active, then updates bounce-buffer attributes and reports features.

## Dependencies and Integration Points
The file depends on confidential-computing attributes, `sme_me_mask`, DMA direct mapping, SWIOTLB, memblock, virtio anchor callbacks, and SEV/SNP helpers. It affects all DMA-capable drivers indirectly through DMA mapping and bounce-buffer policy.

## Risks
Under-sizing SWIOTLB in encrypted guests causes DMA failures or severe performance loss. Overly broad unencrypted DMA policy can reduce protection, while overly narrow policy breaks devices that cannot address encrypted memory. Feature reporting depends on `cc_vendor` and attribute state being initialized correctly.

## Test Signals
Boot logs should show memory encryption features and adjusted SWIOTLB size under SEV/TDX. DMA-heavy workloads in encrypted guests, virtio devices, and devices with limited DMA masks validate the policy. SNP host boots should show successful e820 fixups.
