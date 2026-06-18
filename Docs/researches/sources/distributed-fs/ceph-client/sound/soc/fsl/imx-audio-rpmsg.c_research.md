# sources/distributed-fs/ceph-client/sound/soc/fsl/imx-audio-rpmsg.c

## Purpose
RPMsg bus glue for i.MX audio offload channels. It binds remote-processor audio and micfil RPMsg endpoints, creates the platform PCM component device, creates the `imx-audio-rpmsg` machine-card platform device, and routes remote period notifications or command responses to the PCM RPMsg state.

## APIs, Types, and Functions
`struct imx_audio_rpmsg` stores the spawned PCM and card platform devices. `imx_audio_rpmsg_cb()` handles incoming `struct rpmsg_r_msg` packets. `imx_audio_rpmsg_probe()` registers platform devices named after the RPMsg channel and `imx-audio-rpmsg`; `imx_audio_rpmsg_remove()` unregisters them. The RPMsg ID table matches `rpmsg-audio-channel` and `rpmsg-micfil-channel`.

## Control Flow, State, and Persistence
Probe allocates private state on the RPMsg device, then spawns child platform devices. Incoming type-C notifications update TX/RX period-done message tails under the per-stream spinlock and invoke the stored DMA callback. Type-B responses copy the message into `info->r_msg` and complete `cmd_complete`, unblocking synchronous sends in `imx-pcm-rpmsg.c`. State persists in the child platform device's `struct rpmsg_info`, not in this file.

## Dependencies and Integration
Depends on `linux/rpmsg.h`, platform-device registration, and `imx-pcm-rpmsg.h` protocol structures. It integrates tightly with `imx-pcm-rpmsg.c` via `platform_get_drvdata(rpmsg_pdev)` and with `imx-rpmsg.c` through the card platform device data containing the channel name.

## Risks and Test Signals
Risks include callbacks arriving before the child platform driver has initialized `rpmsg_info`, unchecked callback function pointers, modulo by `num_period` before a stream is fully configured, and partial cleanup if the first child device succeeds and the second registration fails. Test signals are endpoint probe for both channel names, platform child creation, type-B response completion, type-C period elapsed callbacks for playback/capture, and remove without dangling platform devices.
