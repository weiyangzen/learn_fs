# sources/distributed-fs/ceph-client/sound/soc/fsl/pcm030-audio-fabric.c

## Purpose
Machine/fabric driver for the Phytec PCM030 board using the MPC5200 PSC AC97 interface and a WM9712 AC97 codec. It creates analog and IEC958 DAI links and instantiates the legacy codec platform device.

## APIs, Types, and Functions
`struct pcm030_audio_data` stores the card and allocated codec platform device. Static DAI link definitions connect CPU DAIs `mpc5200-psc-ac97.0`/`.1` to `wm9712-codec` DAIs `wm9712-hifi` and `wm9712-aux`. `pcm030_fabric_probe()` validates machine compatibility, assigns platform OF nodes, requests the codec module, creates the codec platform device, and registers the card. Remove unregisters the card and codec device.

## Control Flow, State, and Persistence
Probe only runs on `phytec,pcm030`, reads `asoc-platform`, assigns it to each DAI link platform, loads `snd-soc-wm9712`, allocates/adds `wm9712-codec`, then registers the static `pcm030_card`. State is partly static card/link data and partly per-device `pcm030_audio_data`.

## Dependencies and Integration
Depends on MPC5200 AC97 CPU DAIs from `mpc5200_psc_ac97.c`, WM9712 codec module, OF machine compatibility, and ASoC card registration. The `asoc-platform` phandle ties the fabric to the PSC AC97 platform component.

## Risks and Test Signals
Risks include static card/link structures limiting multi-instance use, manual codec platform-device lifetime, weak handling when `platform_device_alloc()` fails before `platform_device_add()`, and legacy module autoload assumptions. Test signals are probe only on PCM030, WM9712 module load and platform device creation, both AC97 analog and IEC958 links registered, and card removal releasing the codec device.
