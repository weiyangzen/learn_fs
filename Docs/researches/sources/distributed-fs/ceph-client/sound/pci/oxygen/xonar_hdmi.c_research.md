
# sources/distributed-fs/ceph-client/sound/pci/oxygen/xonar_hdmi.c

Purpose: HDMI helper for Xonar HDAV models, communicating with an HDMI controller over Oxygen UART.

Important functions: `hdmi_write_command` frames commands with magic bytes, command, count, params, and checksum. `xonar_hdmi_init_commands` resets UART, sends setup commands, and writes audio params. Public init/cleanup/resume manage HDMI enable state. `xonar_hdmi_pcm_hardware_filter` restricts multichannel playback rates to 44.1/48/96/192 kHz. `xonar_set_hdmi_params` maps ALSA params to IEC958 sample-rate code, channel-pair count, sample width, and sends command 0x54. `xonar_hdmi_uart_input` logs received OK messages.

State/persistence: `xonar_hdmi.params[5]` persists last HDMI audio format for resume. UART input is buffered in shared `oxygen.uart_input`.

Dependencies: `oxygen_write_uart/reset_uart`, ALSA PCM params, IEC958 constants, Xonar PCM179x HDAV model. Risks: checksum/protocol regressions are hard to see without hardware; UART input buffer wraps at 32 bytes. Test signals: HDAV probe, HDMI switch, multichannel hw constraints, playback at supported rates/channel counts/formats, resume, cleanup mute, and debug logs for OK responses.
