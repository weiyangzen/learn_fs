# sources/distributed-fs/ceph-client/sound/soc/soc-compress.c

Purpose: creates and operates ALSA compressed audio devices for ASoC, covering both normal codec-to-CPU links and dynamic front-end/back-end DPCM compressed paths.

Important APIs and data: `soc_compr_ops` handles static compressed streams; `soc_compr_dyn_ops` handles dynamic FE streams. Open/free paths call DAI/component/link startup and shutdown helpers with rollback handling. Trigger, set/get params, ack, pointer, metadata, caps, and optional copy are dispatched across CPU DAI, components, machine link, DPCM BEs, and DAPM as appropriate. `snd_soc_new_compress()` validates unidirectional single CPU/codec support, allocates `snd_compr`, creates optional internal BE PCM for dynamic links, selects ops, enables copy when any component supports it, and registers the compressed device.

Control flow and state: static open gets runtime PM, locks DPCM mutex, starts CPU DAI/components/link, and activates runtime; failure calls `soc_compr_clean()` with rollback. Dynamic FE open computes DPCM paths under card lock, starts BEs, then FE CPU/component/link. Dynamic set_params prepares BEs with empty FE hw_params before programming compressed params. Trigger updates DPCM state and DAPM stream events. Persistent state includes `rtd->compr`, `compr->private_data`, `rtd->fe_compr`, `rtd->pcm` for dynamic links, delayed close work function, DPCM states, and active runtime flags.

Dependencies and integration: depends on ALSA compress core, ASoC DPCM, DAPM, component and DAI compress helpers, and card/runtime locks.

Risks: compressed devices reject multi-CPU or multi-codec links. Dynamic FE correctness depends on lock ordering and DPCM state transitions. Partial drain bypasses BE trigger and only hits components. Error rollback must keep PM/module/component marks balanced.

Test signals: static and dynamic compressed playback/capture open/free, invalid bidirectional or multi-codec rejection, DPCM BE startup/params/trigger ordering, drain commands, metadata/ack/pointer propagation, and copy callback exposure.
