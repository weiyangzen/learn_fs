<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/dmic.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/dmic.c

Purpose: generic AVS DMIC machine driver for Intel PCH digital microphone endpoints.

Important APIs, types, and functions: platform driver `avs_dmic`; `avs_dmic_probe()`; `avs_create_dai_links()`; DAI definitions for `DMIC Pin` and `DMIC WoV Pin`.

Control flow: board selection first creates a `dmic-codec` platform device and passes its device name in `avs_mach_pdata.codec_name`. Probe creates two capture-only backend links sharing the DMIC codec: normal DMIC and wake-on-voice DMIC. The WoV link sets `ignore_suspend` so it can stay available across suspend. The card then registers with DMIC widget/routes and either modern or obsolete names.

State and persistence: no private runtime state beyond the card and link allocations. The codec name is copied from platform data and must remain stable for component matching.

Dependencies and integration points: depends on `SND_SOC_DMIC`, `avs_register_dmic_component()` CPU DAIs, NHLT PDM endpoint detection, and topology `dmic-tplg.bin`.

Risks: the two links share a single allocated codec component descriptor; that is intentional but means both links assume identical codec endpoint. If board selection fails to create `dmic-codec`, probe cannot bind to a codec. WoV suspend behavior must match firmware topology support.

Test signals: two backend links named `DMIC` and `DMIC WoV`, capture works on the normal path, WoV path survives suspend, and no card is created when NHLT has no PDM endpoint.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/dmic.c -->
