## sources/distributed-fs/ceph-client/arch/arm64/include/asm/boot.h

Purpose: documents and exports boot-time placement constraints for arm64 kernel images and device trees.

Important APIs/types/functions: defines `MIN_FDT_ALIGN` as 8, `MAX_FDT_SIZE` as 2 MiB, and `MIN_KIMG_ALIGN` as 2 MiB.

Control flow: constants only.

State and persistence: no runtime state; the constants constrain bootloader and EFI stub placement decisions.

Dependencies and integration: depends on `<linux/sizes.h>`. Used by boot code, EFI, decompression/stub code, and documentation-aligned validation.

Risks: changing these constants can make valid bootloaders fail or allow invalid placements. Test signals include EFI stub boots, non-EFI bootloader boots, DTB placement tests, and image alignment checks.
