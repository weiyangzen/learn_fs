# sources/distributed-fs/ceph-client/include/linux/soc/ti/omap1-soc.h

Purpose: This OMAP1 header defines CPU class, subclass, and type detection helpers for OMAP7xx, OMAP15xx, OMAP16xx, and specific models.

Important APIs/types/functions: It uses `omap_rev()` bit extraction macros and generated inline helpers such as `is_omap15xx`, `is_omap16xx`, model-specific `is_omap310`, `is_omap1510`, `is_omap1610`, `is_omap5912`, and public `cpu_is_omap*` macros. Disabled configs compile unsupported helpers to zero while `cpu_class_is_omap1()` is true for this platform family.

Control flow: Platform and drivers branch on these helpers during initialization to choose clocks, muxes, errata, USB, memory, and peripheral behavior.

State and persistence: The helpers interpret SoC revision state exposed by platform code; no mutable state is stored.

Dependencies and integration: Integrates with OMAP1 platform support, board files, mux, USB, clocks, and legacy drivers.

Risks and test signals: Variant misclassification can program wrong register layouts. Test `omap_rev()` values, compile variants, and boot/probe on each supported OMAP1 subclass.
