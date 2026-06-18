# sources/distributed-fs/ceph-client/sound/soc/sof/pcm.c

Purpose: Implements the ALSA PCM component layer that bridges ASoC PCM operations to SOF topology widgets, IPC-specific PCM ops, and platform DMA ops.

Important APIs/state: `snd_sof_pcm_period_elapsed()` schedules work to call ALSA period elapsed outside IRQ-sensitive IPC timing. `sof_pcm_hw_params()`, `prepare()`, `trigger()`, `hw_free()`, `open()`, `close()`, `pointer()`, `ack()`, `delay()`, and `pcm_new()` populate the `snd_soc_component_driver` in `snd_sof_new_platform_drv()`. State lives in `snd_sof_pcm`: `stream[].list`, `platform_params`, saved `params`, `prepared`, `setup_done`, `pending_stop`, `suspend_ignored`, page tables, and position data.

Control flow: Open sets runtime hardware from platform ops and topology caps, then opens platform DMA. Hw_params boots DSP if needed, handles repeated params by freeing previous setup, calls platform hw_params, prepares connected DAPM widgets, configures host widget DMA, creates page tables when the buffer changes, and saves params. Prepare recreates hw_params after resume/xrun if needed, sets up widgets/routes/pipelines, and calls IPC hw_params. Trigger decides whether IPC or platform DMA starts/stops first, handles D0i3 suspend-ignore and DSPless reset, and may defer STOP cleanup via `pending_stop`. Hw_free stops/free IPC and DMA, frees widgets, unprepares DAPM lists, and cancels period work.

Dependencies and integration: Uses SOF topology/widget helpers, IPC-specific PCM ops, platform PCM ops in `ops.h`, ALSA runtime constraints, DAPM connected-widget walking, PM runtime for topology probe, and SOF page-table helpers.

Risks: Prepared/setup/list flags must remain balanced across repeated hw_params, xruns, suspend, and errors. Trigger ordering differs by IPC ops and can deadlock or underrun if wrong. Period elapsed is delayed to avoid IPC timeout while IRQ thread still handles a previous IPC. BE no-pcm paths are no-ops.

Test signals: Open/close, repeated hw_params without hw_free, buffer_changed page table creation, prepare after xrun, START/STOP/PAUSE/SUSPEND trigger order for IPC3 and IPC4, D0i3-compatible stream suspend-ignore, DSPless mode, pointer fallback paths, topology probe failure, and BE DAI fixup fallback.
