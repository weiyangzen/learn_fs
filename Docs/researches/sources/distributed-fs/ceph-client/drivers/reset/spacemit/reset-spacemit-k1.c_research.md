# sources/distributed-fs/ceph-client/drivers/reset/spacemit/reset-spacemit-k1.c

Purpose: SpacemiT K1 reset table driver exposing MPMU, APBC, APMU, RCPU, RCPU2, and APBC2 reset domains through common CCU reset code.

Important APIs/types/functions: static `ccu_reset_data` arrays encode K1 reset IDs from SpacemiT clock/syscon bindings into register offsets and masks. `K1_AUX_DEV_ID()` builds auxiliary device IDs whose `driver_data` points at domain-specific `ccu_reset_controller_data`. The auxiliary driver uses `spacemit_reset_probe()`.

Control flow: K1 CCU creates matching auxiliary devices; each device registers one reset controller for its domain. Runtime ops are delegated to common regmap mask updates.

State and persistence: tables are static; parent CCU register bits hold reset state. No additional mutable state in this file.

Dependencies and integration: SpacemiT K1 syscon/clock bindings, auxiliary bus, common SpacemiT reset namespace, and parent CCU regmap.

Risks and test signals: table entries with identical offsets and masks for multiple PWM resets may reflect shared hardware but need binding validation. Test all auxiliary IDs, binding/table count alignment, register mask polarity, and module namespace import.
