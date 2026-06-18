# sources/distributed-fs/ceph-client/drivers/clk/clk-gemini.c

Purpose: Cortina Gemini SoC clock and reset controller driver. It supplies early fixed/factor clocks, later gated peripheral clocks, a custom PCI clock, and a self-deasserting reset controller for the Gemini syscon.

Important APIs, types, and functions: `gemini_gate_data` describes gate bits and parent names. `clk_gemini_pci` implements PCI rate, parent, and enable operations using `gemini_pci_clk_ops`. `gemini_reset` implements reset-controller callbacks through `gemini_reset_ops`. `gemini_cc_init()` performs early `CLK_OF_DECLARE_DRIVER` setup, while `gemini_clk_probe()` fills clocks that should defer until the platform driver binds.

Control flow: early init allocates `gemini_clk_data`, initializes all slots to `-EPROBE_DEFER`, reads `GEMINI_GLOBAL_STATUS`, registers `xtal`, `vco`, `ahb`, and `apb`, and exposes the onecell provider. Probe maps the syscon MMIO resource, obtains a regmap, registers the reset controller, derives CPU/security clocks from register fields, registers gate clocks using `CLK_GATE_SET_TO_DISABLE`, then adds TVC, PCI, and UART clocks.

State and persistence: state is held in syscon registers and the global `gemini_clk_data`. Gate bits default to ungated at boot. Reset writes are self-deasserting. No persistent storage exists beyond hardware register state.

Dependencies and integration points: integrates with syscon/regmap, reset-controller, DT bindings for Gemini clock/reset IDs, common clock fixed-rate/factor/gate helpers, and `builtin_platform_driver`.

Risks and test signals: several comments note unclear TVC and PCI parents, so rate accuracy is partly board-knowledge dependent. Gate RMW is protected by `gemini_clk_lock`. Reset status reads a self-clearing register, which may be transient. Test signals are boot probe success, onecell lookup by DT ID, PCI 33/66 MHz switching, and reset-controller consumers.
