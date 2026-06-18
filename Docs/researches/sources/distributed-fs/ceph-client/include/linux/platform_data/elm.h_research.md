
# sources/distributed-fs/ceph-client/include/linux/platform_data/elm.h

## Purpose
This header defines the interface to TI's BCH Error Location Module used by OMAP NAND BCH ECC support. It describes ECC strength, error-vector results, and helper functions for configuring and decoding BCH errors.

## Important APIs And Types
`enum bch_ecc` selects BCH4, BCH8, or BCH16. `ERROR_VECTOR_MAX` is 8. `struct elm_errorvec` records whether a vector reported errors, whether errors were uncorrectable, the correctable error count, and up to 16 error locations. When `CONFIG_MTD_NAND_OMAP_BCH` is enabled, `elm_decode_bch_error_page()` and `elm_config()` are declared; otherwise inline stubs do nothing and return `-ENOSYS`.

## Control Flow, State, And Persistence
Consumers configure the ELM for ECC type, steps, step size, and syndrome size, then submit calculated ECC syndromes for page decode. The ELM driver fills error vectors for NAND correction. Runtime state is hardware configuration and per-page decode output only.

## Dependencies And Integration Points
It integrates OMAP NAND BCH code, MTD, and the ELM hardware driver. It uses Linux device pointers and conditional compilation for optional hardware support.

## Risks And Test Signals
Risks include mismatched BCH strength, wrong ECC step sizing, ignoring `-ENOSYS`, and mishandling uncorrectable vectors. Test signals include NAND read correction tests with injected bitflips, uncorrectable error reporting, build coverage with and without `CONFIG_MTD_NAND_OMAP_BCH`, and ECC layout compatibility.
