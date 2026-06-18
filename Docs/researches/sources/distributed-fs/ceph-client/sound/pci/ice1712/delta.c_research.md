# sources/distributed-fs/ceph-client/sound/pci/ice1712/delta.c

## Purpose
Implements board-specific low-level support for M-Audio Delta-family ICE1712 cards, Digigram VX442, Lionstracs Mediastation, and Edirol DA2496. It plugs these boards into the generic ICE1712 core by declaring `snd_ice1712_delta_cards[]`, setting channel counts, programming GPIO-driven S/PDIF and codec buses, initializing AKM converter descriptions, and adding card-specific ALSA controls.

## Important APIs, Types, and Functions
The public entry point is the `snd_ice1712_delta_cards[]` table. `snd_ice1712_delta_init()` is the main `chip_init` callback and `snd_ice1712_delta_add_controls()` is the mixer/control callback. The file implements an emulated I2C/SPI path for CS8427 through `ap_cs8427_sendbytes()`, `ap_cs8427_readbytes()`, and `ap_cs8427_i2c_ops`; legacy CS8403 S/PDIF status writes through `snd_ice1712_delta_cs8403_spdif_write()`; AKM chip-select callbacks for Delta44/66, Delta1010LT, Delta66E, and VX442; and rate callbacks `delta_1010_set_rate_val()`, `delta_ak4524_set_rate_val()`, and `vx442_ak4524_set_rate_val()`. Optional PM hooks reset/mute and restore AKM/CS8427 state.

## Control Flow
Initialization first normalizes some EEPROM IDs to newer Delta1010E/Delta66E variants based on GPIO direction, sets total DAC/ADC counts by subvendor, installs PM callbacks, and raises the SPI clock line. Boards with CS8427 create an ALSA I2C bus using the GPIO-backed ops and call `snd_ice1712_init_cs8427()`. Older Delta1010/MediaStation or DiO/Delta66 variants use GPIO rate switching and/or CS8403 S/PDIF ops. Boards without analog AKM management return early; others allocate `ice->akm`, select the matching AKM template/private GPIO masks, and call `snd_ice1712_akm4xxx_init()`. Control creation adds word-clock, optical input, S/PDIF, and AKM mixer controls according to subvendor.

## State and Persistence Behavior
Runtime state lives in `struct snd_ice1712`: `num_total_dacs`, `num_total_adcs`, `i2c`, `cs8427`, `akm`, `akm_codecs`, `spdif.cs8403_bits`, and GPIO register shadowing. The CS8403 default and stream status bytes are stored in `ice->spdif` and written immediately when not blocked by an active professional playback stream. AKM register images/volumes are preserved across suspend/resume by copying them before reinitialization. Hardware state is volatile and reconstructed from EEPROM, board subtype, ALSA controls, and AKM/CS8427 caches.

## Dependencies and Integration Points
The file depends on the ICE1712 core helpers from `ice1712.h`, GPIO bit definitions from `delta.h`, ALSA I2C, CS8427, CS8403 helpers, AK4xxx codec support, and ALSA control APIs. It is consumed by `ice1712.c` through `card_tables[]`; the generic probe calls the selected card-info callbacks after base chip setup.

## Risks
GPIO bit sharing is the main risk: CS8427, AKM codecs, word clock, and S/PDIF status all reuse small board-specific pin maps and must hold `gpio_mutex` or save/restore GPIO direction/mask correctly. Rate changes above 48 kHz toggle DFS bits and sometimes reset converters, so regressions can cause clicks, silent audio, or wrong high-rate operation. Subvendor remapping based on `gpiodir` is heuristic. CS8403 status writes are bit-banged with long delays and can conflict with active stream status if locking or stream checks change.

## Test Signals
Probe each listed model or forced `model=` alias, verify expected channel counts and mixer controls, check CS8427 initialization on Audiophile/Delta410/1010LT/66E/VX442, validate S/PDIF default and PCM stream control updates, test word-clock status/select controls on Delta1010 and 1010LT, run playback/capture at <=48 kHz and >48 kHz to confirm DFS behavior, and suspend/resume with AKM mixer volumes and CS8427 state restored.
