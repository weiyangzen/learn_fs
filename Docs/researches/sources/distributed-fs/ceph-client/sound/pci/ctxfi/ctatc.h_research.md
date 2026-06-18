# sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctatc.h

Purpose: public ATC object model and callback interface for the ctxfi subsystem.

Important APIs and types: declares ALSA logical devices `FRONT`, `SURROUND`, `CLFE`, `SIDE`, `IEC958`, `MIXER`; card identification structs; `struct ct_atc_pcm` stream-resource bundle; and `struct ct_atc`, the central operation table and state holder. Public functions are `ct_atc_create` and `ct_atc_create_alsa_devs`.

Control flow and integration: `xfi` probe creates an ATC, then PCM and mixer layers use the callback table for stream prepare/start/stop/position, route selection, mute, S/PDIF status, and capabilities. PM builds store `struct snd_pcm *pcms` for resume interaction.

State and persistence: header defines all major runtime state: resource manager array, mixer, hardware object, VM, DAIO/PCM/SRC/SRCIMP persistent resources, stream resources, PLL rate, model name, and RCA state.

Risks and test signals: broad function-pointer API means initialization must fully populate `atc_preset`; missing callbacks fail later and indirectly. Test construction, all callback invocations used by PCM/mixer controls, and PM compile/runtime paths.
