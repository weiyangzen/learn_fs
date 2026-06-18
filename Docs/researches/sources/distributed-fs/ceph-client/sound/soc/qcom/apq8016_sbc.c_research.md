# sources/distributed-fs/ceph-client/sound/soc/qcom/apq8016_sbc.c

Purpose: implements APQ8016 SBC and MSM8916 QDSP6 machine-driver setup for MI2S routing, jack detection, backend ops, and sound-card registration.

Important APIs/types/functions: `struct apq8016_sbc_data` stores card, IOMUX registers, jack, setup flag, and MI2S clock reference counts. Important functions are `apq8016_dai_init`, `apq8016_sbc_add_ops`, `msm8916_qdsp6_dai_init`, QDSP6 startup/shutdown, backend hw_params fixup, and probe.

Control flow: probe allocates card data, parses DAI links with `qcom_snd_parse_of`, maps mic/spkr IOMUX resources, stores drvdata, applies compatible-specific link ops, and registers the card. DAI init configures MI2S TLMM/IOMUX bits, creates headset jack once, sets button key mappings, sets codec MCLK, and attaches the jack to codecs. QDSP6 backend ops force 48 kHz stereo S16 and reference-count LPAIF bit clock enable per MI2S port.

State and persistence: IOMUX MMIO bits persist board routing; `jack_setup` avoids duplicate jack creation; `mi2s_clk_count[]` keeps shared backend bit clock balanced.

Dependencies and integration: depends on Qualcomm common OF parser, dt-bindings for APQ8016 LPASS/Q6AFE IDs, QDSP6 AFE IDs, codec jack support, and resources named `mic-iomux` and `spkr-iomux`.

Risks: reference counts are not explicitly locked. IOMUX writes are read-modify-write without regmap locking. `qdsp6_dai_get_lpass_id` must stay synchronized with QDSP6 DAI IDs. Default MCLK and fixed BE params may not suit nonstandard codecs.

Test signals: card probe for both compatibles, MI2S route playback/capture, jack insertion/button events, QDSP6 backend clock count balance across concurrent streams, and fixed BE hw_params negotiation.
