# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_main.c

Purpose: is the platform driver entry point and top-level IPA orchestration layer. It probes hardware, selects firmware loading mode, initializes subsystems, configures registers/resources, performs setup with immediate commands, and tears everything down.

Important APIs/functions: `ipa_probe()` is the main initialization state machine. `ipa_setup()` initializes GSI, endpoint programming, AP command and exception endpoints, memory/table setup, default route, and QMI setup. `ipa_config()` handles powered register configuration, memory config, interrupts, microcontroller, endpoint/resource config, and SSR notifier registration. `ipa_remove()` shuts down modem traffic, setup, config, and all initialized subsystems. Hardware helpers program BCR, TX config, clock-on workarounds, COMP_CFG, QSB limits, aggregation/Qtime timing, hashing/cache behavior, and dynamic clock division. `ipa_firmware_load()` loads MDT firmware to reserved memory and authenticates via SCM.

Control flow: probe obtains matched `ipa_data`, resolves loader mode (`self`, `modem`, `skip`, legacy `modem-init`), initializes interrupt/power/IPA object/registers/memory/cmd/GSI/endpoints/table/SMP2P, takes runtime PM, runs `ipa_config()`, then either waits for modem SMP2P setup-ready or loads firmware and calls `ipa_setup()`. Setup enables the command endpoint first because later steps issue immediate commands, then enables the LAN exception endpoint and starts QMI handshake.

State/persistence: `struct ipa` stores device, version, power, interrupt, memory mappings, GSI, endpoint maps/bitmaps, modem route count, setup flag, and completion. Hardware register state persists until deconfig/reset; runtime PM autosuspend gates access.

Dependencies/integration: integrates Linux platform/of/module/firmware/PM APIs, Qualcomm SCM/MDT loader, IPA data tables, GSI, command, memory, tables, resources, modem, SMP2P, QMI, microcontroller, sysfs attribute groups, and register metadata.

Risks: probe has many staged resources; unwind ordering is critical. Firmware loader properties are mutually constrained, and SCM availability can defer probe. `ipa_remove()` can leak resources if modem stop repeatedly fails. Version-specific register programming must match the matched `ipa_data`.

Test signals: platform probe succeeds on listed compatibles, firmware load paths behave for self/modem/skip modes, sysfs groups appear, runtime PM autosuspends/resumes, modem setup completes after QMI, and remove/shutdown do not warn or leak initialized subsystems.
