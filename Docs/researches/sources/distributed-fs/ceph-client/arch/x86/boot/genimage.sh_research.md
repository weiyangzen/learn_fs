# sources/distributed-fs/ceph-client/arch/x86/boot/genimage.sh

Purpose: build helper for `make bzdisk`, floppy images, hard-disk images, and ISO images around an x86 bzImage plus optional initrds and command line.

Important APIs and state: shell entry arguments are disk format, output image, bzImage, mtools config, command line, and initrds. Functions include `verify`, `die`, `le`, `efiarch`, `filesizes`, `sharedirs`, `efidirs`, `findsyslinux`, `findovmf`, `do_mcopy`, `genbzdisk`, `genfdimage144`, `genfdimage288`, `genhdimage`, and `geniso`. State is temporary shell variables and generated image files.

Control flow: validates the kernel image, gathers readable initrds, detects EFI architecture from PE headers, finds syslinux/isolinux/OVMF assets, removes any previous output image, and dispatches by requested format. Disk-image paths use mtools/syslinux; ISO path builds a temporary isolinux tree and runs `genisoimage` plus optional `isohybrid`.

Dependencies and integration: invoked by arch/x86 boot Makefile targets. Requires bash, syslinux/isolinux, mtools, genisoimage, and sometimes OVMF/EDK2 shell. `mtools.conf.in` supplies drive mappings.

Risks and test signals: external tool availability and distro-specific asset paths are the main risks. The script intentionally sends `USR1` to its top shell on fatal errors. Test each image target, initrd option generation for syslinux/EFI, EFI arch detection, missing-tool failure messages, and cleanup of temporary ISO directory.
