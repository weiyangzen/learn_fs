# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_tis_core.h

## Purpose
Defines the shared TIS register layout, status bits, interrupt bits, quirks, private data, PHY interface, inline endian-aware register helpers, and exported core entry points.

## Important APIs, Types, And Functions
Key types are `enum tis_access`, `enum tis_status`, `enum tis_int_flags`, `enum tis_defaults`, `enum tpm_tis_flags`, `struct tpm_tis_data`, `enum tpm_tis_io_mode`, and `struct tpm_tis_phy_ops`. Inline helpers wrap PHY reads/writes for 8/16/32-bit little-endian access and optional CRC verification.

## Control Flow
The header defines address macros such as `TPM_ACCESS(l)`, `TPM_STS(l)`, `TPM_DATA_FIFO(l)`, `TPM_DID_VID(l)`, and `TPM_RID(l)` that all PHY front-ends use. `is_bsw()` provides an x86 Bay Trail check for CLKRUN handling.

## State And Persistence
`struct tpm_tis_data` is the persistent runtime object for each TIS chip while the driver is bound, carrying chip pointer, locality state, IRQ bookkeeping, waitqueues, PHY ops, and timing details.

## Dependencies And Integration Points
Included by MMIO, SPI, I2C, SynQuacer, and core TIS files. Exports `tpm_tis_core_init()`, `tpm_tis_remove()`, and, under PM, `tpm_tis_resume()`.

## Risks And Edge Cases
Address macros encode locality shifts differently from some bus-specific protocols, so front-ends must translate carefully. PHY ops promise little-endian data; violating that breaks core register interpretation. `is_bsw()` depends on x86 CPU model definitions.

## Test Signals
Build coverage across all TIS PHYs, endian conversion tests for 16/32-bit helpers, CRC callback behavior, locality address calculation, and PM conditional declarations.
