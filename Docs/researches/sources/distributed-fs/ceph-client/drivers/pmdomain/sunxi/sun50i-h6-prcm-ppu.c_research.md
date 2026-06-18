<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/sunxi/sun50i-h6-prcm-ppu.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/sunxi/sun50i-h6-prcm-ppu.c

Purpose: Allwinner H6/H616 PRCM power-domain provider for a small set of PRCM-controlled rails, notably GPU and analog/system rails. It exposes fixed register-bit domains through the generic PM domain framework.

Important APIs/types/functions: `struct sun50i_h6_ppu_pd` wraps `generic_pm_domain` with an MMIO register, gate mask, and negated-bit flag. `sun50i_h6_ppu_desc` and `sun50i_h6_ppu_data` describe SoC-specific domain names, offsets, masks, and flags. `sun50i_h6_ppu_power_status()`, `sun50i_h6_ppu_pd_set_power()`, `sun50i_h6_ppu_pd_power_on()`, and `sun50i_h6_ppu_pd_power_off()` implement bit-level power state. `sun50i_h6_ppu_probe()` allocates onecell genpd data, maps PRCM registers, initializes each domain, and registers `of_genpd_add_provider_onecell()`.

Control flow: probe selects match data for `allwinner,sun50i-h6-prcm-ppu` or `allwinner,sun50i-h616-prcm-ppu`, allocates domain arrays, maps resource 0, then iterates descriptors. For each domain it computes `base + offset - PD_H6_PPU_OFFSET`, sets callbacks and `GENPD_FLAG_ALWAYS_ON` when required, initializes with current hardware state, and publishes a onecell provider. Error unwind removes already initialized domains.

State/persistence: no persistent software state beyond devm allocations and genpd registration. Runtime state is the PRCM gate bit, with H616 domains using `FLAG_PPU_NEGATED` where set bit means off rather than on. Initial genpd off state is inferred from the register.

Dependencies/integration: depends on platform device probing, DT compatible data, `devm_platform_ioremap_resource()`, generic PM domains, and Allwinner PRCM register layout. Bind attributes are suppressed because active power domains cannot be removed safely.

Risks: register offsets are deliberately expressed relative to the full PRCM block and adjusted by `PD_H6_PPU_OFFSET`; a wrong DT resource base or descriptor offset will write the wrong PRCM bit. No polling confirms that a rail actually settled after a bit write. Negated semantics are SoC-specific and easy to regress.

Test signals: boot on H6/H616 with GPU/consumer devices using `power-domains`; confirm provider registration, initial state detection, on/off callbacks, and no writes to `GENPD_FLAG_ALWAYS_ON` rails during suspend/runtime PM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/sunxi/sun50i-h6-prcm-ppu.c -->
