# sources/distributed-fs/ceph-client/drivers/ata/sata_gemini.c

## Purpose
`sata_gemini.c` controls the Cortina Systems Gemini SATA bridge that connects SATA adapters to Faraday FTIDE010 ATA controllers. It is not a libata host driver itself; it is a platform bridge driver exporting helper APIs used by the Gemini FTIDE010 path.

## Important APIs, Types, and Functions
The key state container is `struct sata_gemini`, holding device, MMIO base, mux mode, feature booleans, and SATA0/SATA1 PCLK handles. Exported APIs are `gemini_sata_bridge_get()`, `gemini_sata_bridge_enabled()`, `gemini_sata_get_muxmode()`, `gemini_sata_start_bridge()`, and `gemini_sata_stop_bridge()`. Probe helpers include `gemini_sata_setup_bridge()`, `gemini_sata_bridge_init()`, `gemini_setup_ide_pins()`, `gemini_sata_probe()`, and `gemini_sata_remove()`.

## Control Flow, State, and Persistence
Probe allocates singleton state, maps bridge registers, obtains the global syscon, optionally initializes SATA bridge clocks and reads bridge IDs, optionally enables IDE pins, validates and stores the DT mux mode, writes global IDE mux bits through regmap, selects the IDE pinctrl state when requested, sets platform drvdata, and publishes `sg_singleton`. Starting a bridge enables its PCLK, waits, programs SATA0/1 control bits including slave mode for mux modes 2 or 3, waits up to one second for PHY-ready status, and disables the clock again on failure. Stop disables the selected bridge clock.

## Dependencies and Integration Points
The file depends on platform/OF properties, syscon regmap, common clock framework, pinctrl, MMIO register access, and exported GPL symbols consumed by the Gemini ATA host driver. Device-tree properties include `cortina,gemini-enable-sata-bridge`, `cortina,gemini-enable-ide-pins`, and `cortina,gemini-ata-muxmode`.

## Risks and Test Signals
Risks include singleton ordering causing `-EPROBE_DEFER` loops, mux modes disconnecting an ATA controller from SATA unexpectedly, clock prepare/enable imbalance, missing cleanup if IDE pin selection fails after clocks are prepared, and no explicit bridge disable register write on stop. Tests should cover all four mux modes, SATA-only, IDE-only, and mixed configurations, deferred consumers before bridge probe, PHY-ready timeout, clock failure paths, remove/unprepare behavior, and DT validation for missing syscon or illegal mux mode.
