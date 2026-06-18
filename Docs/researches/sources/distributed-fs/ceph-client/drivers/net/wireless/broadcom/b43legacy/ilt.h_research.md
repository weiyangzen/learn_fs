# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/ilt.h

## Purpose
Declares b43legacy initial lookup-table sizes, exported table symbols, and ILT register access helpers. It is the public interface between PHY calibration code and the table data in `ilt.c`.

## Important APIs, Types, and Functions
Size macros include `B43legacy_ILT_ROTOR_SIZE`, `B43legacy_ILT_RETARD_SIZE`, `B43legacy_ILT_FINEFREQA_SIZE`, `B43legacy_ILT_FINEFREQG_SIZE`, `B43legacy_ILT_NOISEA2_SIZE`, `B43legacy_ILT_NOISEA3_SIZE`, `B43legacy_ILT_NOISEG1_SIZE`, `B43legacy_ILT_NOISEG2_SIZE`, `B43legacy_ILT_NOISESCALEG_SIZE`, and `B43legacy_ILT_SIGMASQR_SIZE`. It declares all matching `extern const` arrays and the helpers `b43legacy_ilt_write`, `b43legacy_ilt_write32`, and `b43legacy_ilt_read`.

## Control Flow
No runtime control flow exists in the header. Consumers use size macros to bound table iteration and helper prototypes to access hardware ILT registers.

## State and Persistence
The header declares immutable table state and hardware-mutating helper APIs. The actual persistent state is in the device PHY ILT registers after writes performed by callers.

## Dependencies and Integration Points
Requires `struct b43legacy_wldev` from included driver headers through consumers. It integrates with `ilt.c` and PHY/radio code that loads calibration constants into the hardware.

## Risks
Size macro drift from actual arrays can cause truncated initialization or out-of-bounds iteration. Because the arrays represent hardware calibration constants, consumers should not reinterpret units or signedness without checking PHY code expectations.

## Test Signals
Compile-time references from PHY code, successful table iteration during PHY init, and stable device calibration after cold start are the main checks. Build warnings for missing symbols catch mismatches with `ilt.c`.
