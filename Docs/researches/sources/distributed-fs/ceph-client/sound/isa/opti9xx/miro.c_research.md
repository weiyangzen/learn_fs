# sources/distributed-fs/ceph-client/sound/isa/opti9xx/miro.c

## Purpose
`miro.c` is the ALSA driver for Miro miroSOUND PCM1 pro, PCM12, and PCM20 Radio cards. It combines OPTi 82C924/82C929 WSS configuration with a Miro ACI command/mixer interface, optional MPU401, optional OPL4, proc reporting, ISA/PnP probing, and card-model-dependent controls.

## Important APIs, Types, and Functions
- `struct snd_miro` stores OPTi hardware information, management-control resources, WSS/IRQ/DMA/MPU settings, card pointer, and ACI pointer.
- ACI API: `snd_aci_cmd` and `snd_aci_get_aci` are exported; internal helpers `aci_busy_wait`, `aci_write`, `aci_read`, `aci_getvalue`, and `aci_setvalue` serialize access with `aci_mutex`.
- Mixer callbacks handle capture solo mode, preamp, line amp, stereo volumes, seven-band EQ, radio/line controls, and model-specific additions.
- Probe flow: `snd_card_miro_detect`, `snd_card_miro_aci_detect`, `snd_miro_configure`, `snd_miro_probe`, `snd_miro_isa_probe`, and `snd_miro_pnp_probe`.

## Control Flow
Legacy ISA creates a card, detects the OPTi chip through passworded management registers, auto-finds WSS/MPU/IRQ/DMA resources when requested, detects ACI at port `0x344` or `0x354`, initializes ACI, configures OPTi WSS and MPU routing, creates WSS PCM/mixer/timer, adds Miro ACI mixer controls according to product ID, optionally creates MPU401 and OPL4, applies ACI defaults, and registers the card. PnP activates audio/MPU/MC devices, fills the same global resource variables, initializes as 82C924, and uses the same probe path.

## State and Persistence
ACI state is held in a single static `aci_device`, including vendor/product/version, port, mutex, and cached amp/preamp/solomode. Runtime resources and mixer state are in `struct snd_miro`; proc output reports current values. No persistent storage is used.

## Dependencies and Integration Points
The driver integrates Linux ISA/PnP, ALSA WSS/MPU401/OPL4/control/proc APIs, legacy resource finders, and the public ACI header. Exported ACI access can be used by related code.

## Risks and Test Signals
Risks include the static single ACI device limiting concurrency, long sleeps in `aci_busy_wait`, mutable global module-resource variables after PnP detection, unimplemented suspend/resume, and product-ID-specific mixer registration. Test signals include PCM1/PCM12/PCM20 detection, ACI ID/version reads, ACI mixer get/put round trips, WSS mode and IDE enable options, proc report correctness, PnP fallback to ISA, and OPL4/MPU optional-device failure tolerance.
