<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/Kconfig

## Purpose
Defines the TPM driver configuration surface: the common TCG TPM core, TPM2 HMAC bus protection, hwrng exposure, TIS/FIFO transports, legacy vendor drivers, CRB, vTPM proxy, TEE fTPM, SVSM vTPM, and the ST33ZP24 subdirectory.

## Important APIs, Types, And Functions
Important symbols are `TCG_TPM`, `TCG_TPM2_HMAC`, `HW_RANDOM_TPM`, `TCG_TIS_CORE`, `TCG_TIS`, `TCG_TIS_SPI`, `TCG_TIS_I2C`, vendor I2C/PNP/platform options, `TCG_CRB`, `TCG_ARM_CRB_FFA`, `TCG_VTPM_PROXY`, `TCG_FTPM_TEE`, `TCG_SVSM`, and `TCG_LOONGSON`. The file uses Kconfig `depends on`, `select`, `imply`, and `source` to connect build options.

## Control Flow
Configuration starts at `menuconfig TCG_TPM`; all child choices are available only when TPM support is enabled. Transport-specific options select common core modules where needed, and optional interfaces gate source compilation through the Makefile.

## State And Persistence
The selected symbols persist in the kernel `.config` and determine compiled-in or module TPM support. They also control runtime availability of securityfs event logs, hwrng integration, encrypted TPM2 transactions, and bus-specific probe code.

## Dependencies And Integration Points
Integrates with ACPI, EFI, OF, I2C, SPI, PNP, XEN, TEE/OP-TEE, AMD memory encryption, MFD Loongson, Arm FF-A, crypto primitives, and securityfs. It sources `drivers/char/tpm/st33zp24/Kconfig` for STMicroelectronics support.

## Risks And Edge Cases
Wrong dependency relationships can expose unbuildable drivers or hide necessary transports. `TCG_TPM2_HMAC` pulls crypto dependencies and changes TPM2 transaction behavior. `HW_RANDOM_TPM` has a built-in/module compatibility constraint against impossible link combinations.

## Test Signals
Useful signals are `allyesconfig`/`allmodconfig` builds across ACPI, OF, I2C, SPI, X86, ARM64, Xen, TEE, and COMPILE_TEST targets, plus boot probes confirming expected `/dev/tpm*`, `/dev/tpmrm*`, securityfs logs, and hwrng behavior for selected symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/Kconfig -->
