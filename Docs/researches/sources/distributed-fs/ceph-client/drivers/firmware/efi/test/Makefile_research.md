# sources/distributed-fs/ceph-client/drivers/firmware/efi/test/Makefile

Purpose: Builds the EFI runtime service test misc driver when `CONFIG_EFI_TEST` is enabled.

Important APIs/types/functions: The only build rule is `obj-$(CONFIG_EFI_TEST) += efi_test.o`, binding the Kconfig option to `efi_test.c`.

Control flow: No runtime control flow. Kbuild includes the object in built-in or module output according to the tristate value selected by configuration.

State and persistence behavior: No state. It determines whether the `/dev/efi_test` interface code is present in the kernel/module build.

Dependencies and integration points: Integrates with the EFI firmware driver subtree and Kbuild. It assumes the source file exports a normal module init/exit pair.

Risks and test signals: Risk is limited to build coverage; a stale object name or missing Kconfig symbol would silently omit the test driver. Test by enabling `CONFIG_EFI_TEST=m/y`, building, and confirming `efi_test.ko` or built-in registration.
