# sources/distributed-fs/ceph-client/arch/mips/econet/Kconfig

Purpose: defines EcoNet MIPS SoC and devicetree configuration choices.

Important symbols: under `if ECONET`, `SOC_ECONET_EN751221` selects common clock, EcoNet interrupt controller, PCI support, generic PCI drivers, MIPS CPU IRQs, SMP, SMP_UP, and SMP support. `DTB_ECONET_NONE` leaves no built-in DTB; `DTB_ECONET_SMARTFIBER_XP8421_B` depends on the EN751221 family and selects `BUILTIN_DTB`.

Control flow and integration: Kconfig choices drive which platform features and built-in DTB are compiled. The help text documents EN7512/RN7513/EN7521/EN7526 family assumptions and SmartFiber XP8421-B boot packaging.

Risks and test signals: selecting SMP/SMP_UP for single-core 34Kc systems is intentional but easy to misread. Kconfig tests should verify dependencies select required IRQ/clock/PCI support and built-in DTB inclusion.
