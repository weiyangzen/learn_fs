# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/include/soc.h

Purpose: Defines small Broadcom SoC/backplane constants for enumeration base, common core control flags, and common core status flags.

Important APIs/constants: `SI_ENUM_BASE_DEFAULT` gives the default SI enumeration base. `SICF_*` defines BIST, PME, core-bit, force-gated-clock, and clock-enable control flags. `SISF_*` defines BIST done/error, gated clock, DMA64, and core status bits.

Control flow and state: No executable flow. Values are used for low-level core control/status register manipulation.

Dependencies and integration: Standalone include, consumed by PMU/AI/core reset and clock paths. Risks include incorrect bit values causing failed core reset, wrong clock gating, or BIST handling problems. Test signals include core enumeration, reset/clock enable sequences, BIST status checks, and DMA64-capability detection.
