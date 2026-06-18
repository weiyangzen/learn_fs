# sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_wm8804.c

Purpose: SOF machine driver for UP/UP2 boards using WM8804/Hifiberry Digi+ SPDIF hardware on SSP5.

Important APIs, types, and functions: `struct sof_card_private` stores two optional clock-select GPIOs and cached sample rate. DMI quirk `SOF_WM8804_UP2_QUIRK` enables UP2-specific GPIO lookup. `sof_wm8804_hw_params()` computes MCLK frequency/divider from sample rate, selects SPDIF status sampling-frequency bits, toggles 44.1 kHz or 48 kHz oscillator GPIOs, programs WM8804 MCLK divider, PLL, sysclk, and status register. Probe resolves the ACPI codec device name dynamically from `mach->id`, optionally installs a GPIO lookup table and obtains the two GPIOs, sets card drvdata, and registers the one-link card.

Control flow and integration: Static link connects `SSP5 Pin` to `wm8804-spdif`. Runtime hw_params only reprograms when sample rate changes. Remove removes the UP2 GPIO lookup table.

State and persistence: Private cached sample rate and GPIO descriptors are devm-managed except the global lookup table. Static codec name buffer and link component name are mutated at probe. No persistent state.

Dependencies: WM8804 codec APIs/registers, ACPI device lookup, DMI, GPIO lookup/consumer APIs, ASoC DAI ops, and PM ops.

Risks: GPIO lookup uses platform-specific ACPI GPIO controller indices and is mandatory on UP2 quirk systems. Unsupported sample rates fail. Codec-name mutation is static. Test signals include 44.1/48 kHz family oscillator switching, SPDIF sample-rate status bits, all supported rates through 192 kHz, ACPI codec name fixup, and GPIO cleanup on remove.
