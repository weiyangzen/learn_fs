<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/Makefile -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/Makefile

## Purpose
Builds the TPM core object and maps Kconfig symbols to TPM transport, vendor, virtual, and firmware-backed driver modules.

## Important APIs, Types, And Functions
The aggregate `tpm.o` includes `tpm-chip.o`, `tpm-dev-common.o`, `tpm-dev.o`, `tpm-interface.o`, `tpm1-cmd.o`, `tpm2-cmd.o`, `tpmrm-dev.o`, `tpm2-space.o`, `tpm-sysfs.o`, eventlog code, `tpm-buf.o`, and `tpm2-sessions.o`. Conditional additions include `tpm_ppi.o`, eventlog ACPI/EFI/OF readers, TIS, I2C/SPI variants, ST33ZP24, CRB/FF-A, vTPM, fTPM TEE, SVSM, and Loongson modules.

## Control Flow
Kbuild evaluates `obj-$(CONFIG_...)` lines to compile selected modules. The common `tpm.o` core is built when `CONFIG_TCG_TPM` is enabled; transport drivers then register `struct tpm_chip` instances through exported TPM core APIs.

## State And Persistence
The Makefile has no runtime state. Its persistent effect is the object composition and module names exposed to kernel packaging and modprobe.

## Dependencies And Integration Points
It is tightly coupled to `Kconfig` symbols and the source layout in `drivers/char/tpm/`, including the `st33zp24/` subdirectory. The eventlog objects are conditionally folded into the common core depending on firmware interface support.

## Risks And Edge Cases
Missing object references can compile a feature without required helpers, while stale object names break module builds. Conditional eventlog inclusion must match the inline stubs in `eventlog/common.h`.

## Test Signals
Build TPM as built-in and as modules across ACPI, EFI, OF, I2C, SPI, CRB, and ST33ZP24 configs. Module load tests should confirm expected names such as `tpm`, `tpm_crb`, `tpm_st33zp24_i2c`, and `tpm_st33zp24_spi`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/Makefile -->
