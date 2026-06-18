# sources/distributed-fs/ceph-client/sound/soc/sof/pm.c

Purpose: Implements SOF firmware boot orchestration and runtime/system power-management flows.

Important APIs/state: `snd_sof_boot_dsp_firmware()` serializes boot with `dsp_fw_boot_mutex`, loads/runs firmware, resumes trace, restores pipelines, resumes clients, and calls IPC context restore. `sof_resume()` and `sof_suspend()` drive platform PM callbacks, firmware state transitions, trace suspend/resume, pipeline tear-down/setup, D0/D3 target selection, and on-demand boot. Exported wrappers provide runtime/system suspend/resume/idle, prepare/complete, and power-down notification. Module parameter `on_demand_boot` can override descriptor behavior.

Control flow: Power target maps S3/S4/S5 to D3, S0ix to D0 only if streams ignored suspend, and runtime to D3. Resume skips first boot, powers platform, handles DSPless, resumes trace only for D0 substate resume, optionally defers boot for on-demand mode, otherwise boots firmware. Suspend tears down pipelines if old state is D0, skips firmware notifications when not complete, sets hw_params-upon-resume for system suspend, suspends trace and clients, sends ctx_save unless staying in D0, calls platform suspend, and resets FW state/enabled cores on D3. Prepare derives suspend target from ACPI when enabled.

Dependencies and integration: Uses IPC PM ops, topology ops, platform DSP ops, trace helpers, SOF clients, ACPI target states, and PCM suspend-ignore state from `sof-audio.c`.

Risks: Firmware state is central; incorrect transitions can cause double boot or lost resume. `ctx_save` `-EBUSY/-EAGAIN` is propagated only for runtime PM; other errors continue to power down. On-demand boot defers firmware until PCM hw_params. Pipeline tear-down is attempted before state checks when old hardware state is D0. Debugfs cache is conditional and only captures D0-only entries when enabled.

Test signals: Runtime suspend/resume, S0ix with and without suspend-ignored streams, S3/S4/S5 targets, on-demand boot override, DSPless mode, ctx_save busy/error paths, crashed/boot-failed prepare behavior, trace suspend/resume failures, and pipeline restore failure cleanup.
