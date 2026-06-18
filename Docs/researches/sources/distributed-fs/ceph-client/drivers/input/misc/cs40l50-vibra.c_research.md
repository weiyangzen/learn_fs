<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/cs40l50-vibra.c -->
## sources/distributed-fs/ceph-client/drivers/input/misc/cs40l50-vibra.c

Purpose: advanced force-feedback haptic input driver for Cirrus CS40L50 MFD devices, supporting ROM/RAM/open-wavetable effects, GPIO trigger mapping, and ordered playback commands to the DSP.

Important APIs/types/functions: `struct cs40l50_vibra` stores device, regmap, input, ordered workqueue, uploaded effect list, and DSP register/command description. `cs40l50_add()` uploads or updates FF_CUSTOM periodic effects through `cs40l50_add_worker()`. `cs40l50_playback()` queues start/stop workers. `cs40l50_erase()` removes mappings/effects and deletes OWT entries. Helpers select bank/index, configure GPIO triggers, and upload OWT headers/data.

Control flow and state: probe gets parent MFD data, creates an input FF device with one effect slot, installs upload/playback/erase callbacks, initializes the effect list, allocates an ordered high-priority workqueue, and registers input. Upload and erase use stack work plus flush to provide synchronous input-core semantics while serializing with playback. Playback allocates async work and writes DSP commands for the requested count or stop command.

State and persistence behavior: uploaded effects are tracked in `effect_head`; OWT uploads and GPIO mappings persist in DSP/register state until erased or reset. Runtime PM is acquired around DSP operations and released with autosuspend.

Dependencies and integration points: depends on CS40L50 MFD definitions and `cs40l50_dsp_write`, regmap, Linux input FF periodic/custom APIs, ordered workqueues, runtime PM, and platform device ID `cs40l50-vibra`.

Risks: only one effect slot is supported. `cs40l50_stop_worker()` leaks `work_data` if runtime resume fails. OWT indexing is compacted by decrementing later tracked indexes and assumes DSP delete has the same compaction behavior. Playback repeat uses `replay.length` as a microsecond sleep interval, so unit assumptions should be validated. GPIO register calculation trusts encoded trigger button bits.

Test signals: test ROM/RAM/OWT upload validation, OWT no-space handling, GPIO mapping and disable on erase, playback count and stop, runtime PM failure paths, ordered serialization between upload/play/erase, and effect-list compaction after OWT deletion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/cs40l50-vibra.c -->
