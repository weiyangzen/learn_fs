# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_tis_spi.h

## Purpose
Defines the SPI PHY structure and exported helper/probe functions shared by the generic TIS SPI driver and the Cr50 SPI specialization.

## Important APIs, Types, And Functions
Defines `struct tpm_tis_spi_phy` with embedded `tpm_tis_data`, SPI device pointer, flow-control callback, completion, wake timing, and I/O buffer. Declares `tpm_tis_spi_init()`, `tpm_tis_spi_transfer()`, `cr50_spi_probe()`, and optional `tpm_tis_spi_resume()`.

## Control Flow
The inline `to_tpm_tis_spi_phy()` converts from core data to SPI PHY. Conditional stubs allow the generic SPI driver to compile without Cr50 support.

## State And Persistence
The PHY struct persists for the lifetime of an SPI TPM device and carries both generic SPI transaction state and Cr50-specific wake/ready fields used by the specialized implementation.

## Dependencies And Integration Points
Included by `tpm_tis_spi_main.c` and `tpm_tis_spi_cr50.c`, and depends on the TIS core interface.

## Risks And Edge Cases
The flow-control callback is mandatory for transfers; front-ends must initialize it. Conditional stubs mean device IDs can resolve to `-ENODEV` when Cr50 support is disabled.

## Test Signals
Build matrix with and without `CONFIG_TCG_TIS_SPI_CR50`, SPI probe dispatch for generic and Cr50 IDs, and resume declaration under PM.
