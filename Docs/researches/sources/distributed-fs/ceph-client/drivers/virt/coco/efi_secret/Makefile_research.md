# sources/distributed-fs/ceph-client/drivers/virt/coco/efi_secret/Makefile

## Purpose
Builds the EFI secret-area driver.

## APIs, Types, and Functions
Maps `CONFIG_EFI_SECRET` to `efi_secret.o`.

## Control Flow and State
No runtime behavior in this file.

## Dependencies and Integration
Used by the CoCo parent Makefile.

## Risks and Test Signals
Build both built-in and module variants and verify module alias `platform:efi_secret` comes from the C file.
