<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/arizona-spi.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/arizona-spi.c

Purpose: provides the SPI transport binding for Arizona-class codecs, including special ACPI board handling for WM5102 devices. It selects chip-specific SPI regmap configuration, fills platform data quirks for ACPI systems, and delegates common initialization to the Arizona core.

Important APIs and functions: `arizona_spi_probe` and `arizona_spi_remove` are the driver lifecycle functions. ACPI helpers include `arizona_spi_acpi_probe`, `arizona_spi_acpi_windows_probe`, `arizona_spi_acpi_android_probe`, and lookup-table cleanup `arizona_spi_acpi_remove_lookup`. Static ACPI microphone-detect ranges provide AOSP button resistance mappings.

Control flow: probe gets match data from SPI/OF/ACPI, selects a regmap config for WM5102, WM5110/WM8280, or WM1831/CS47L24 if enabled, allocates `struct arizona`, initializes SPI regmap, stores type/device/IRQ, applies ACPI quirks when present, and calls `arizona_dev_init`. Windows-style ACPI setup maps reset/LDO GPIO resources, adds lookup-table entries for SoC GPIOs, invokes a CLKE ACPI method, sets IRQ trigger low, and populates mic-detect/headphone-detect defaults. Android-style ACPI setup defers when reset GPIO lookup is not yet available.

State and persistence: bus-specific state is the allocated `struct arizona` and SPI regmap. ACPI paths may install devm-managed GPIO mappings and platform-data fields before core initialization. Persistent codec power/register state is managed by `arizona-core.c`.

Dependencies and integration points: depends on SPI, regmap, OF, ACPI, GPIO descriptor/machine lookup APIs, input key codes for mic button mappings, PM ops from the core, and chip regmap configs declared in `arizona.h`. It has a soft dependency on `arizona_ldo1`.

Risks: ACPI board quirk behavior is broad and assumes known Windows/Android firmware patterns. The driver forces ACPI IRQ flags to active-low level because falling-edge DSDT entries are known broken; unsupported hardware with true edge-only wiring would need another workaround. Probe deferral for Android reset GPIO depends on external lookup-table providers. Unsupported Kconfig variants fail before core probe.

Test signals: SPI modalias/OF/ACPI matching, regmap initialization for supported chip types, Windows and Android ACPI board probe paths, reset/LDO GPIO mapping, CLKE method warnings, IRQ trigger correction, mic-detect button reporting through child drivers, and core probe/remove behavior over SPI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/arizona-spi.c -->
