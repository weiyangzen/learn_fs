<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/soc-link.h -->
# sources/distributed-fs/ceph-client/include/sound/soc-link.h

## Purpose
`soc-link.h` declares ASoC DAI-link lifecycle helpers. It centralizes link-level init/exit, BE hw_params fixups, PCM callbacks, triggers, and compressed stream callbacks.

## Important APIs, types, and functions
APIs are `snd_soc_link_init()`, `snd_soc_link_exit()`, `snd_soc_link_be_hw_params_fixup()`, `snd_soc_link_startup()`, `snd_soc_link_shutdown()`, `snd_soc_link_prepare()`, `snd_soc_link_hw_params()`, `snd_soc_link_hw_free()`, `snd_soc_link_trigger()`, `snd_soc_link_compr_startup()`, `snd_soc_link_compr_shutdown()`, and `snd_soc_link_compr_set_params()`.

## Control flow
The ASoC PCM/compress core invokes these wrappers at runtime. They call the machine driver's link operations, apply backend parameter fixups, and participate in rollback-aware startup/shutdown/hw_free/trigger sequencing.

## State and persistence behavior
The header has no state. It mutates runtime state held by `snd_soc_pcm_runtime`, DAI links, and stream objects through implementation code.

## Dependencies and integration points
It integrates `snd_soc_dai_link` callbacks from `soc.h` with PCM, compressed-audio, DPCM, component, and DAI runtime sequencing.

## Risks and test signals
Risks include rollback mismatches, missing BE fixup propagation, compressed and PCM path divergence, link callback returning success after partial setup, and trigger order regressions. Test signals include link ops for startup/hw_params/prepare/trigger/hw_free/shutdown, BE fixup failures, compressed streams, rollback on each failure point, and dynamic DPCM FE/BE links.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/soc-link.h -->
