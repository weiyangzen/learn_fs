# sources/distributed-fs/ceph-client/include/linux/soc/samsung/exynos-chipid.h

Purpose: This Samsung Exynos header defines CHIPID register offsets and bitfields, especially for Exynos5422 binning, speed group, and auxiliary info.

Important APIs/types/functions: It defines PRO_ID, PKG_ID, LOT_ID, AUX_INFO offsets, revision masks/shifts, Exynos ID mask, and Exynos5422 fields for IDS, speed group, table, SG_A/SG_B, sign, bin2, TMCB, and ARM/KFC up/down values.

Control flow: The Exynos chipid driver reads these registers, decodes SoC identity and ASV/binning data, then publishes it to SoC/OPP/thermal or debug code.

State and persistence: CHIPID registers are read-only or fuse-derived SoC identity state that persists for the device lifetime.

Dependencies and integration: Integrates with Samsung Exynos socinfo, ASV/OPP, thermal, and platform detection code.

Risks and test signals: Incorrect field extraction can choose wrong voltage/frequency bins. Test register decode against known silicon, revision masking, and OPP/ASV consumers.
