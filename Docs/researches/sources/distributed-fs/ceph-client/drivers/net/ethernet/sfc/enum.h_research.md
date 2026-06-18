# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/enum.h

Purpose: Defines shared enumerations and masks for loopback modes and reset types used across SFC PHY, selftest, ethtool, reset, and port code.

Important APIs and definitions: `enum efx_loopback_mode` lists controller, PHY, external, and wireside loopbacks. Macros define internal/wireside/external masks and predicates such as `LOOPBACK_INTERNAL()`, `LOOPBACK_EXTERNAL()`, `LOOPBACK_CHANGED()`, and `LOOPBACK_OUT_OF()`. `enum reset_type` distinguishes reset methods/scopes from reset reasons, including MCDI timeout as a special method outside the normal scope hierarchy.

Control flow and integration: Loopback predicates drive port reconfiguration, PHY transmit disable decisions, and test selection. Reset type ordering is used by `efx_schedule_reset()` and `efx_reset()` to select and clear pending reset scopes.

State and persistence: No state. The numeric values are semantically important because reset methods are ordered by increasing scope and loopback modes index name tables and masks.

Dependencies: Standalone include guard; consumed by shared driver headers and implementation files.

Risks: Reordering enum values breaks masks, string tables, reset scope clearing, and user-visible diagnostics. The comment typo for `RESET_TYPE_INVISIBLE` does not affect behavior but can mislead documentation readers.

Test signals: Selftest loopback enumeration, ethtool loopback configuration, port reconfiguration for internal/external transitions, reset scheduling for each reason/method, and string-table bounds checks.
