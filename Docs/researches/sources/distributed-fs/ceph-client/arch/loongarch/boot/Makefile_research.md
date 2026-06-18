# sources/distributed-fs/ceph-client/arch/loongarch/boot/Makefile

## Purpose

`Makefile` builds LoongArch boot images from `vmlinux`, including stripped `vmlinux.elf`, EFI images, and EFI zboot payload metadata. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

Important build variables include `OBJCOPYFLAGS_vmlinux.efi`, `EFI_ZBOOT_PAYLOAD`, `EFI_ZBOOT_BFD_TARGET`, and image targets `vmlinux.elf`/`vmlinux.efi`. Concrete declarations observed in the file: Build/script rules: `drop-sections := .comment .note .options .note.gnu.build-id`, `strip-flags   := $(addprefix --remove-section=,$(drop-sections)) -S`, `OBJCOPYFLAGS_vmlinux.efi := -O binary $(strip-flags)`, `quiet_cmd_strip = STRIP	  $@`, `cmd_strip = $(STRIP) -s -o $@ $<`, `targets := vmlinux.elf`, `$(obj)/vmlinux.elf: vmlinux FORCE`, `targets += vmlinux.efi`, `$(obj)/vmlinux.efi: vmlinux FORCE`, `EFI_ZBOOT_PAYLOAD      := vmlinux.efi`, `EFI_ZBOOT_BFD_TARGET   := elf32-loongarch`, `EFI_ZBOOT_MACH_TYPE    := LOONGARCH32`, `EFI_ZBOOT_BFD_TARGET   := elf64-loongarch`, `EFI_ZBOOT_MACH_TYPE    := LOONGARCH64`.

## Control Flow, State, And Persistence

Build flow invokes objcopy with section removal for boot images and selects 32-bit or 64-bit EFI zboot metadata from configuration.

## Dependencies And Integration Points

It integrates with the top-level LoongArch Makefile, EFI stub/zboot infrastructure, and kernel install targets.

## Risks And Test Signals

Risks are wrong BFD target, stripping required sections, or mismatched EFI machine type. Test signals are `make vmlinux.elf`, `make vmlinux.efi`, zboot builds, and `file/readelf` image inspection.
 A local static signal for this file is that it has 33 lines and 818 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
