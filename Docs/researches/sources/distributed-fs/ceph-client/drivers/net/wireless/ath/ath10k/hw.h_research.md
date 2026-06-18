# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/hw.h

## Purpose

`hw.h` is the central ath10k hardware contract header. It declares bus and hardware revision identities, firmware and board file naming constants, firmware/board IE formats, per-chip register/value structures, hardware parameter structures, operation hooks, target resource constants, register-address macros, and low-level bit masks used by bus, boot, HTT, WMI, LED, RFKill, survey, and diagnostic code.

## Important APIs, Types, and Declarations

- Hardware identity: `enum ath10k_bus`, `enum ath10k_hw_rev`, QCA/WCN device IDs, chip revision enums, firmware directory/version macros.
- Firmware formats: `struct ath10k_fw_ie`, `enum ath10k_fw_ie_type`, `enum ath10k_fw_wmi_op_version`, `enum ath10k_fw_htt_op_version`, board IE enums.
- Register/value tables: `struct ath10k_hw_regs`, `struct ath10k_hw_values`, `struct ath10k_hw_ce_*`, extern declarations for `qca*` and `wcn3990` tables.
- Runtime parameters: `struct ath10k_hw_params` captures feature flags, firmware directory/board sizes, RX descriptor ops, hardware ops, target capacities, descriptor mode, checksum/ring parameters, SAR/restart behavior, and bus quirks.
- Operation hooks: `struct ath10k_hw_ops` plus inline wrappers `ath10k_tx_data_rssi_get_pad_bytes()` and `ath10k_is_rssi_enable()`.
- Public functions: `ath10k_hw_fill_survey_time()` and `ath10k_hw_diag_fast_download()`.
- Macros: `QCA_REV_*()`, target resource constants for MAIN/10.x/TLV/HL/10.4 firmware, CE/MSI constants, register base/address/mask aliases, PLL masks, coverage-class registers, and diagnostic CPU address window helpers.

## Control Flow

This header has no executable control flow beyond two inline wrappers. It shapes control flow elsewhere by letting device match code populate `ar->hw_params`, `ar->regs`, and `ar->hw_values`, after which generic code accesses hardware through common macros such as `RTC_SOC_BASE_ADDRESS`, `CE_COUNT`, `PCIE_INTR_CE_MASK_ALL`, and `CCNT_TO_MSEC()`. Optional operations are called only when function pointers are non-NULL; missing RSSI hooks return zero.

The target-resource macros define firmware configuration payload sizes and limits sent by WMI startup code. The revision macros gate chip-specific code paths. The register macros abstract per-chip base addresses by expanding through `ar->regs`, while legacy/MBOX aliases preserve compatibility with older code using pre-ath10k naming.

## State and Persistence Behavior

The header defines state layouts but does not allocate persistent state. `struct ath10k_hw_params` instances persist per device in memory and drive feature behavior for the lifetime of the driver instance. Extern tables are read-only constants defined in `hw.c` or other compilation units. Macro reads depend on live `ar->regs`, `ar->hw_values`, and `ar->hw_params` pointers.

## Dependencies and Integration Points

`hw.h` depends on `targaddrs.h` and forward declarations for HTT and RX descriptor structs. It is included across ath10k core, bus, HTC/HTT, WMI, debug, firmware-loading, and hardware-control code. Its definitions connect firmware image parsing to loader code, hardware tables to bus register programming, target resource counts to WMI init, and HTT descriptor/RSSI behavior to RX/TX completion logic.

## Risks

- Many macros assume an `ar` variable is in scope, which is convenient but fragile for refactors.
- `QCA9377_1_0_DEVICE_ID` shares value with `QCA6174_3_2_DEVICE_ID`; callers must disambiguate by other context.
- `MISSING` placeholder aliases expand to zero and can be dangerous if used on unsupported paths.
- `struct ath10k_hw_params` is broad and feature-dense; adding a field requires auditing all hardware table initializers for correct defaults.
- Target constants encode firmware resource contracts. Mistakes can cause startup failures, peer/TID exhaustion, descriptor pool pressure, or mismatched firmware expectations.
- Register address macros mix absolute constants and table-derived addresses; using the wrong family path can silently program the wrong location.

## Test Signals

Tests should compile all bus/config combinations, validate hardware table initializers against `struct ath10k_hw_params` changes, exercise each `QCA_REV_*()` branch, verify WMI target resource payloads for MAIN/10.x/TLV/HL/10.4, confirm optional hw_ops wrappers with NULL/non-NULL callbacks, assert diagnostic window mask math, and catch accidental use of `MISSING` register aliases on active code paths. Build warnings, sparse/clang diagnostics, boot-time register access failures, and firmware startup resource errors are the main signals.
