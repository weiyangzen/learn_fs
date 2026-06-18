# sources/distributed-fs/ceph-client/drivers/phy/socionext/phy-uniphier-usb3hs.c

Purpose: UniPhier USB3 high-speed PHY provider, responsible for USB2/HS-side PHY clocks, resets, tuning, optional nvmem trim, and VBUS.

Important APIs, types, and functions: `struct uniphier_u3hsphy_soc_data` supplies legacy flag, parameter list, default config registers, and trim callback. `uniphier_u3hsphy_get_nvparam(s)` reads `rterm`, `sel_t`, and `hs_i` cells. `uniphier_u3hsphy_update_config()` applies trim or default disconnect threshold. `uniphier_u3hsphy_set_param()` writes indirect CFG1 fields. Generic PHY ops implement init/exit and power on/off.

Control flow: probe maps MMIO, obtains `phy`/optional `phy-ext` clock and `phy` reset for non-legacy devices or GIO parent clock/reset for legacy, always obtains `link` clock/reset, optional VBUS, creates one PHY, and registers simple xlate. Init enables parent clocks/resets, skips programming for legacy or zero configs, otherwise updates config0 from nvmem/defaults, writes config0/config1, and applies parameter table. Power-on enables ext and PHY clocks, deasserts PHY reset, then enables VBUS. Exit and power-off unwind.

State and persistence: per-device private data holds clocks/resets/VBUS and SoC table. Hardware trim state is programmed into HSPHY CFG registers and indirect parameter fields. NVMEM values are read at init time and not cached separately.

Dependencies and integration points: generic PHY, clock/reset/regulator APIs, nvmem consumer API, platform DT compatibles for Pro5/PXs2/LD20/PXs3/NX1, USB3 controller HS side.

Risks: nvmem errors other than probe deferral are treated as debug fallback, so bad trim wiring may silently use defaults. Parameter writes use read-modify-write through a narrow indirect data field, sensitive to field masks. Legacy devices skip most programming, relying on external setup.

Test signals: USB2 HS enumeration through USB3 controller, nvmem trim present/absent cases, PLL/clock/reset sequencing under repeated init/exit, VBUS regulator balance, and register dumps of CFG0/CFG1 for LD20/PXs3.
