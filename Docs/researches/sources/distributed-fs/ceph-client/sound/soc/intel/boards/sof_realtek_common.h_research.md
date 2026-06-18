# sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_realtek_common.h

Purpose: Header exposing Realtek amplifier DAI names, component names, and link helper APIs for Intel SOF board drivers.

Important APIs, types, and functions: It defines constants for RT1011, RT1015P, RT1015, RT1308, and RT1019P codec DAI names and ACPI-derived device names. It declares DAI-link patch helpers and codec-conf helpers for families needing card-level name prefixes.

Control flow and integration: Machine drivers include this header and switch on detected codec/amp type, using these functions to fill `ctx->amp_link` after common board-link allocation.

State and persistence: No mutable state is declared here.

Dependencies: ASoC and Intel ACPI SSP common codec IDs.

Risks: Component strings and DAI names are cross-file contracts with codec drivers and ACPI match tables. Test signals include compile coverage across all Realtek amp users and runtime link binding for each codec family.
