# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_audio.h

Purpose: Declares the public DP audio object and HDMI-codec callbacks.

Important APIs/types: `struct msm_dp_audio` stores current lane count and bandwidth code. `msm_dp_audio_get()`/`msm_dp_audio_put()` manage allocation. `msm_dp_audio_prepare()` and `msm_dp_audio_shutdown()` are bridge/codec callbacks for enabling and disabling audio.

Control flow/state: Display code owns the returned object, updates link fields as modes are configured, and exposes prepare/shutdown to the audio codec path.

Dependencies/integration: Includes platform device and HDMI codec headers, forward-declares `drm_bridge`, and integrates with DP display bridge code.

Risks and test signals: Public state is minimal and assumes the caller updates link parameters before prepare. Build and runtime tests should cover HDMI-codec integration and hot unplug during audio.
