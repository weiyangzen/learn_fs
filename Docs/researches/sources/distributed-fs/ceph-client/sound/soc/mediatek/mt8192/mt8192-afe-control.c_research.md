# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8192/mt8192-afe-control.c

This file provides shared sample-rate encoding helpers and a generic per-DAI private-data allocator. `mt8192_general_rate_transform()` maps common audio rates from 8 kHz through 384 kHz to general AFE register values. `dai_memif_rate_transform()` handles the narrow DAI/Modem DAI memif encoding, and `pcm_rate_transform()` handles PCM interface encodings. `mt8192_rate_transform()` selects the specialized transform based on the aud block id.

The functions are used by FE memif setup, IRQ setup, PCM DAIs, I2S DAIs, and other hw_params paths. Invalid rates do not fail; they warn and return a default register code. `mt8192_dai_set_priv()` allocates a devm-owned private blob, copies default data if provided, and stores it in `afe_priv->dai_priv[id]`.

State is limited to mutation of `dai_priv[]`; rate transforms are stateless. Main risks are silent defaulting of invalid rates and lack of bounds checking on `id` in `mt8192_dai_set_priv()`. Test signals include ALSA constraints rejecting unsupported rates before hw_params, correct encodings for 44.1-kHz and 48-kHz families, and all DAI-private initializers passing valid ids.
