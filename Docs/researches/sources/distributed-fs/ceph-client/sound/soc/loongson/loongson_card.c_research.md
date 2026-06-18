# sources/distributed-fs/ceph-client/sound/soc/loongson/loongson_card.c

## Purpose
Implements the Loongson generic ASoC machine driver that binds a Loongson I2S CPU DAI to a codec described by ACPI or devicetree.

## Important APIs, Types, And Functions
`struct loongson_card_data` embeds `snd_soc_card` and stores `mclk_fs`. `loongson_card_hw_params()` programs CPU and codec sysclks from sample rate times `mclk_fs`. `loongson_card_parse_acpi()` resolves `cpu` and `codec` ACPI property references and builds an I2C codec name. `loongson_card_parse_of()` reads `cpu` and `codec` child nodes with `snd_soc_of_get_dlc()`. `loongson_asoc_card_probe()` assembles and registers the card.

## Control Flow, State, And Persistence
Probe allocates card data, reads required `model` and `mclk-fs`, selects ACPI or OF parsing, patches the static DAI link, and registers the card. Runtime state is limited to `mclk_fs` and the static `codec_name` buffer.

## Dependencies And Integration Points
Depends on CPU DAI `loongson-i2s`, codec DAI names from firmware, ACPI property references or OF child nodes, ASoC card registration, and sysclk support on both CPU and codec DAIs.

## Risks And Test Signals
Risks include static global `codec_name` not supporting multiple cards, required `mclk-fs` even when zero might be desirable, ACPI physical-node deferral, and DAI format fixed to I2S inverted bit clock/non-inverted frame with codec/provider clocking. Test signals include ACPI and OF card registration, sysclk calls at several rates, deferred probe of CPU/codec, and multiple-card compile/runtime review.
