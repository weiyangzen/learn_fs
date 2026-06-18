# sources/distributed-fs/ceph-client/sound/soc/sof/sof-of-dev.c

Purpose: generic OF/Device Tree front-end for SOF DSP platform drivers. It translates a platform device match into `snd_sof_pdata`, applies optional deprecated module-parameter file overrides, and delegates probe/remove/shutdown to the common SOF device core.

Important APIs/functions: `sof_of_probe()` allocates `snd_sof_pdata`, obtains the `sof_dev_desc` from `device_get_match_data()`, validates descriptor ops, fills IPC default and firmware/topology override profile fields, installs `sof_of_probe_complete()`, and calls `snd_sof_device_probe()`. `sof_of_probe_complete()` enables runtime PM and autosuspend after successful core probe. `sof_of_remove()` disables runtime PM and removes the core device; `sof_of_shutdown()` forwards shutdown. `sof_of_pm` exports common prepare/complete/system/runtime PM callbacks.

Control flow/state: state is devm-allocated and owned by the platform device. Runtime PM is only enabled after SOF core probe completion. File path/name module parameters are read-only and described as deprecated because the main `snd-sof` module owns them.

Dependencies/integration: depends on OF match data supplied by platform-specific SOF drivers, SOF core `snd_sof_device_*` helpers, and runtime PM. Exported symbols let per-SoC OF drivers share this boilerplate.

Risks/test signals: probe fails early without match data or descriptor ops. Runtime PM disable in remove should be paired with the completion path; test failed probe paths to ensure PM is not disabled/enabled inconsistently. Device Tree binding tests should verify descriptor availability, firmware/topology override handling, suspend/resume, runtime idle, and shutdown.
