# sources/distributed-fs/ceph-client/include/trace/events/asoc.h

## Purpose
`asoc.h` traces ALSA System-on-Chip DAPM power sequencing, widget/path walking, and jack reporting. It helps diagnose audio routing, power transitions, and jack state changes.

## Important APIs, types, and functions
The header defines DAPM formatting helpers `DAPM_DIRECT` and `DAPM_ARROW()`, exports `SND_SOC_DAPM_DIR_OUT`, and declares event classes for DAPM bias levels, DAPM start/done, and widget power/events. Individual events include `snd_soc_dapm_walk_done`, `snd_soc_dapm_path`, `snd_soc_dapm_connected`, `snd_soc_jack_irq`, `snd_soc_jack_report`, and `snd_soc_jack_notify`.

## Control flow
Tracepoints fire at the beginning and end of DAPM bias and graph walks, for widget event start/done/power changes, while checking graph paths, and when jack IRQ/report/notify paths run. Event assignment copies card/component/widget/jack names into trace strings.

## State and persistence behavior
The header owns no state. Records snapshot DAPM context names, card stats counters, widget/path connection flags, stream direction, jack mask/value, and event ids.

## Dependencies and integration points
It depends on ASoC internals via forward-declared card/widget/path structures, `<sound/jack.h>`, `<sound/pcm.h>`, and tracepoint support. It integrates with DAPM graph debugging and userspace trace analysis of audio power behavior.

## Risks and test signals
Risks include dereferencing incomplete DAPM paths, assuming jack->jack is valid, and truncated diagnostic value when names are missing. Test signals are trace sequences for stream startup/shutdown, widget power events, path counts, and jack IRQ-to-report transitions.
