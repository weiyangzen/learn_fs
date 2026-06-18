# sources/distributed-fs/ceph-client/arch/sh/boot/romimage/Makefile



Source read size: 30 lines, 902 bytes.



Purpose: builds SH `romImage` artifacts suitable for flash/MMC boot by combining early ROM setup, zero-page contents, optional MMCIF loader, and the existing zImage.

Important APIs/types/functions: targets `vmlinux`, `zeropage.bin`, `piggy.o`, load address selection, `CONFIG_ROMIMAGE_MMCIF`, and SH7724 ILRAM load address `0xe5200000`.

Control flow: links `head.o`, optional board loader object, and a binary payload built from `.empty_zero_page` plus `arch/sh/boot/zImage`; objcopy extracts the zero page for the embedded payload.

State and persistence: produces ROM boot artifacts only; load address selection determines where the temporary loader executes.

Dependencies and integration points: depends on Kbuild binary linker rules, the SH kernel linker script, `mach/romimage.h`, optional SH7724 MMCIF boot helper, and the zImage target.

Risks and test signals: incorrect load address or zero-page extraction breaks ROM boot. Test by building `CONFIG_ROMIMAGE_MMCIF`, checking `romstart` entry, and booting from flash or MMC at the documented sector offset.
