<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/hdaudio.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/hdaudio.c

Purpose: generic ASoC machine driver for HDA codecs discovered by the AVS HDA bus, including HDMI/display codecs.

Important APIs, types, and functions: platform driver `avs_hdaudio`; `avs_hdaudio_probe()`; dynamic link creator `avs_create_dai_links()`; probing binder link `probing_link`; `avs_probing_link_init()`; HDMI mapping helpers `avs_card_hdmi_pcm_at()` and `avs_card_late_probe()`.

Control flow: board selection creates one platform device per HDA codec with `avs_mach_pdata.codec`. Probe checks the codec device is still registered, creates a temporary "probing-LINK" against `codec-probing-DAI`, and registers the card. During link init, the codec's `pcm_list_head` is counted and converted into real backend DAI links, one per `hda_pcm`. For display codecs, late probe maps HDA HDMI converter PCMs to topology FE PCMs named with the `HDMI` prefix and then completes codec probing.

State and persistence: `hda_pcm->pcm` and `hda_pcm->device` are updated for HDMI codecs during late probe. Card naming is either legacy `hdaudioB%dD%d` or modern `AVS HDMI`/`AVS HD-Audio`.

Dependencies and integration points: depends on HDA codec core, AVS HDA component registration, topology FE naming convention (`HDMI%d`), codec PCM list population, and display power/i915 integration from the core driver.

Risks: dynamic `snd_soc_add_pcm_runtimes()` depends on codec PCM list stability. HDMI topology indexing is 1-based and string parsed; missing topology PCMs produce warnings and invalid devices. Codec removal before deferred card probe is explicitly handled with `-ENODEV`.

Test signals: HDA codec cards bind after codec configure, HDMI converter mapping logs show converter-to-PCM assignment, missing HDMI topology entries warn, and non-display HDA codecs register as "AVS HD-Audio".
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/hdaudio.c -->
