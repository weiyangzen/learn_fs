# sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l45-tables.c

Purpose: CS35L45 register tables and exported utility functions shared by the I2C/SPI wrappers and ASoC core.

Important APIs and data: `cs35l45_patch` is an initialization patch with protected test-key unlock writes, boost/LDPM/clock/test register updates, and error-release defaults. `cs35l45_apply_patch()` registers that patch. `cs35l45_defaults` seeds the regcache with block enables, GPIO defaults, wake/source clock defaults, ASP controls, mixer defaults, DSP stream rates, IRQ masks, and amplifier controls. `cs35l45_i2c_regmap` and `cs35l45_spi_regmap` export 32-bit big-endian regmap configs; SPI adds 16 pad bits. `cs35l45_get_clk_freq_id()` maps supported PLL reference frequencies to hardware configuration IDs.

Control flow: the common core calls `cs35l45_apply_patch()` during device initialization after OTP boot and ID validation. DAI/sysclk logic calls `cs35l45_get_clk_freq_id()` before programming `CS35L45_REFCLK_INPUT`. Regmap callbacks gate cache and register access: readable covers device IDs, power, GPIO, ASP, mixer, IRQ, mailbox, DSP system, and DSP memory regions; volatile covers IDs, reset, status/IRQ/mailbox/DSP scratch and all DSP memory windows.

State and persistence: persistent data is static const table data and exported regmap configurations. Runtime hardware state is not stored here, but cache defaults influence resume and regcache sync behavior.

Dependencies and integration: depends on regmap and `cs35l45.h`; exports symbols in namespace `SND_SOC_CS35L45`. The table module is required by both transport drivers and by `cs35l45.c`.

Risks: register range declarations are broad and must match hardware documentation; an incorrect volatile/readable classification can break regcache resume or block legitimate firmware access. Patch sequencing includes protected magic registers and is sensitive to ordering. PLL frequency support is table-limited; unsupported BCLK/sysclk values fail later DAI setup.

Test signals: compile/link coverage for namespace exports, probe logs showing patch application, regmap cache sync after runtime resume, and DAI parameter tests across every frequency in `cs35l45_pll_refclk_freq`.
