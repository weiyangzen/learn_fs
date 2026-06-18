# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/acpi.h

## Purpose
Defines the ACPI-facing data contracts for the Realtek `rtw89` wireless driver. The header describes DSM function IDs, regulatory and 6 GHz policy payloads, antenna gain and SAR result layouts, vendor ACPI method names, SAR table recognition metadata, geo-SAR table formats, and the public ACPI evaluator entry points used by the rest of the driver.

## Important APIs, Types, and Functions
Key types are `struct rtw89_acpi_data`, `struct rtw89_acpi_dsm_result`, `struct rtw89_acpi_rtag_result`, `struct rtw89_acpi_sar_recognition`, `struct rtw89_acpi_geo_sar_handler`, and the packed policy/SAR records such as `rtw89_acpi_policy_6ghz`, `rtw89_acpi_policy_6ghz_sp`, `rtw89_acpi_policy_6ghz_vlp`, `rtw89_acpi_policy_tas`, `rtw89_acpi_policy_reg_rules`, `rtw89_acpi_static_sar_hdr`, and `rtw89_acpi_dynamic_sar_hdr`. Important enums include DSM function selectors for 6 GHz disable/blocking, TAS, U-NII-4, regulatory rules, VLP, and standard-power policy, plus HP/RT SAR customer IDs and legacy versus 6 GHz-aware SAR revisions. Public functions declared here are `rtw89_acpi_sar_get_subband`, `rtw89_acpi_sar_subband_to_band`, `rtw89_acpi_evaluate_dsm`, `rtw89_acpi_evaluate_rtag`, `rtw89_acpi_evaluate_sar`, and `rtw89_acpi_evaluate_dynamic_sar_indicator`.

## Control Flow
This header has no executable flow itself. It defines the payloads consumed by ACPI implementation code: callers evaluate DSM functions into `rtw89_acpi_dsm_result`, evaluate RTAG antenna gain into `rtw89_acpi_rtag_result`, and evaluate WRDS/RWRD/RWSI/RWGS SAR methods into `struct rtw89_sar_cfg_acpi`. Recognition records bind a customer ID, revision, RF-path-to-antenna mapping, normalization callback, optional geo-SAR handler, and load callback so the implementation can parse different vendor table variants through one dispatch path.

## State and Persistence Behavior
All persistent state modeled here comes from firmware/BIOS ACPI tables and is copied into runtime `rtw89` SAR, TAS, regulation, and antenna-gain structures. Flexible arrays use `__counted_by` for ACPI buffers and policy country lists, while `__packed` keeps ACPI wire layout stable. `rtw89_acpi_dsm_result` holds either a scalar byte or allocated policy pointers; its comment makes caller ownership explicit for dynamically returned policy data.

## Dependencies and Integration Points
The header includes `core.h` for central driver types and constants such as SAR subband counts, RF paths, regulation domains, and antenna-gain dimensions. It integrates with the ACPI implementation file, SAR power limit code, TAS logic, regulatory/country handling, chip capability checks, and platform BIOS methods named `WRDS`, `RWRD`, `RWSI`, and `RWGS`.

## Risks
The packed structs are firmware/BIOS ABI. Reordering fields, changing sizes, or changing counted array semantics can break parsing of vendor ACPI payloads. The `u8` size guards in `RTW89_ACPI_SAR_SIZE_OF()` and `RTW89_ACPI_GEO_SAR_SIZE_OF()` imply table sizes must stay within ACPI format limits. Ownership of allocated policy pointers is easy to miss. Country policy logic is compact and bitmask-driven, so adding countries or policy revisions requires matching parser and regulation behavior.

## Test Signals
Useful signals include boot on systems with and without each DSM function, 6 GHz enable/disable and VLP/SP policy changes, TAS enablement by country, U-NII-4 and UK regulatory rule overrides, RTAG antenna gain parsing, WRDS/RWRD static and dynamic SAR parsing for HP and RT table revisions, RWSI dynamic SAR indicator changes, RWGS geo-SAR region selection, malformed/short ACPI buffers, and suspend/resume with dynamic SAR reevaluation.
