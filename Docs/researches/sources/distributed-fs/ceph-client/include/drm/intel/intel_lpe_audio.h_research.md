# sources/distributed-fs/ceph-client/include/drm/intel/intel_lpe_audio.h

Purpose: describes platform data exchanged with the Intel HDMI LPE audio platform device used on some low-power Intel SoCs.

Important APIs/types/functions: `HDMI_MAX_ELD_BYTES` is 128. `struct intel_hdmi_lpe_audio_port_pdata` carries ELD bytes, port, pipe, link-symbol clock, and DisplayPort/HDMI output flag. `struct intel_hdmi_lpe_audio_pdata` contains three port records for ports B/C/D, number of ports, number of pipes, a `notify_audio_lpe()` callback, and `lpe_audio_slock`.

Control flow: display code fills/updates ELD and port/pipe metadata, notifies the LPE audio platform device on relevant port changes, and protects shared audio state with the spinlock.

State and persistence: runtime ELD and routing state lives in platform data. It changes on hotplug/modeset and is not persistent across driver lifecycle.

Dependencies and integration: depends on Linux types, spinlock types, and `struct platform_device`. Integrated by Intel display/audio glue and the HDMI LPE audio driver.

Risks and test signals: stale ELD, wrong port indexing, and missing locking can break audio routing. Test hotplug, DP vs HDMI output flagging, all three ports, concurrent notification, and sample-rate/ELD propagation to userspace audio.
