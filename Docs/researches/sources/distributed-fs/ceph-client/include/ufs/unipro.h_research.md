<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/ufs/unipro.h -->
# sources/distributed-fs/ceph-client/include/ufs/unipro.h

Purpose: provides UniPro/M-PHY attribute IDs, timing conversion macros, power-mode enums, gear/lane tags, adaptation/equalization constants, and data/network/transport layer attribute definitions used by UFS link setup and tuning.

Important APIs and types: constants cover local/peer M-TX and M-RX attributes, common block attributes, PHY adapter attributes, vendor-specific attributes, TX equalization training, RX eye monitor, timeout defaults, data/network/transport layer attributes, CPort flags, and connection states. Enums define UFS operation mode, PA power modes, HS series, PWM/HS gears, lane count, UniPro versions, TX EQ presets, preshoot/deemphasis levels, and eye-mask types.

Control flow: UFS core and variant drivers issue DME get/set commands using these attribute IDs during link startup, power-mode negotiation, hibern8 entry/exit, gear changes, timeout setup, TX equalization, and error recovery.

State and persistence: no state is stored here. Attribute values live in host/device UniPro and M-PHY hardware registers and may be cached in `ufs_hba`.

Dependencies and integration points: uses bit macros from the broader kernel include environment and integrates with `ufshcd_dme_*()` wrappers, UFS power-mode negotiation, PHY drivers, vendor tuning code, and UFSHCI UIC commands.

Risks and test signals: risks include wrong attribute IDs, lane selector math, time unit conversion, gear-version gating, TX EQ bit packing, and vendor-specific attributes applied to the wrong PHY. Test DME get/set on local and peer attributes, HS/PWM gear switches, hibern8 timing quirks, TX equalization training, and UniPro version compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/ufs/unipro.h -->
