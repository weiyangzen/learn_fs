# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/Kconfig

## Purpose
This Kconfig file defines Intel QuickAssist Technology driver symbols, including the shared `CRYPTO_DEV_QAT` core and multiple physical/virtual device families.

## Important APIs, Types, And Functions
- `CRYPTO_DEV_QAT` is a hidden tristate selected by all QAT device drivers and selects crypto/compression dependencies, firmware loader, and CRC8.
- Device symbols include DH895xCC, C3XXX, C62X, QAT_4XXX, QAT_420XX, QAT_6XXX, and VF variants for older devices.
- Physical-function symbols depend on PCI and endian/architecture constraints, then select `CRYPTO_DEV_QAT`.
- VF symbols also select `PCI_IOV`.
- `CRYPTO_DEV_QAT_ERROR_INJECTION` enables debugfs heartbeat error injection for developer testing.

## Control Flow
Selecting a device-family symbol causes Kbuild to enter the matching subdirectory via the QAT Makefile and build family-specific PCI/hardware-data code plus common QAT infrastructure.

## State And Persistence
No runtime state is stored here. Symbols control compile-time inclusion and module availability.

## Dependencies And Integration Points
The file integrates with `drivers/crypto/intel/qat/Makefile`, QAT common code, PCI/SRIOV, Crypto API algorithms, firmware loading, and compression dependencies such as ZSTD.

## Risks
- The hidden common symbol selects many Crypto API capabilities; enabling any QAT family expands kernel/module dependencies.
- Device support under `COMPILE_TEST` cannot validate firmware loading or accelerator runtime behavior.

## Test Signals
- Build selected PF and VF symbols as modules.
- Confirm `CRYPTO_DEV_QAT_420XX` produces the `qat_420xx` module and pulls in `qat_common`.
- For error injection, confirm debugfs entries exist only with `DEBUG_FS` and the option enabled.
