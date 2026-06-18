# sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_bridge_cs35l56.c

## Purpose
SoundWire utility sidecar support for systems using a CS42L43 bridge codec connected over ASP to two CS35L56 smart amplifiers. It adds a codec-to-codec bridge DAI link, speaker DAPM routes, codec prefixes, TDM/sysclk setup, and amp counting for generic machine drivers.

## APIs, Types, and Functions
Exports `asoc_sdw_bridge_cs35l56_count_sidecar()`, `asoc_sdw_bridge_cs35l56_add_sidecar()`, and `asoc_sdw_bridge_cs35l56_spk_init()`. Internal init `asoc_sdw_bridge_cs35l56_asp_init()` configures the bridge link. Static data includes speaker widget/route maps, name prefixes `AMPL`/`AMPR`, codec-to-codec params, and `bridge_dai_template`.

## Control Flow, State, and Persistence
When the machine context quirk `SOC_SDW_SIDECAR_AMPS` is set, count-sidecar increments DAI and codec-conf counts. Add-sidecar copies the DAI template, fills codec configuration entries for the left/right CS35L56 SPI devices with name prefixes, then advances caller pointers. Runtime init adds the bridge speaker widget/routes, applies CS35L56 volume limits by component prefix, sets codec TDM slots to two RX/TX masks over four 16-bit slots, sets codec sysclk to 3.072 MHz, and mirrors TDM slot setup to CPU DAIs. Speaker init increments `info->amp_num` by two when sidecar amps are present.

## Dependencies and Integration
Depends on ASoC DAPM/DAI/card APIs, generic SoundWire utility structures, `asoc_sdw_mc_private`, `SOC_SDW_SIDECAR_AMPS`, and `asoc_sdw_cs35l56_volume_limit()`. It integrates with machine-driver link allocation through exported `SND_SOC_SDW_UTILS` helpers.

## Risks and Test Signals
Risks include hard-coded component names (`cs42l43-codec`, `spi-cs35l56-left/right`), fixed 48 kHz/16-bit/4-slot bridge parameters, pointer arithmetic contract with caller-allocated DAI/config arrays, and assuming both amplifiers are present. Test signals are quirk-on/off card construction, bridge DAI link registration, DAPM route creation to both amps, TDM/sysclk calls on codec and CPU DAIs, volume-limit application, and amp count consistency.
