# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_event.c

Purpose: formats and rate-limits Komeda hardware events and optional DRM state dumps.

Important APIs/types/functions: exported `komeda_print_events()`. Internal `komeda_sprintf()` appends bounded text, `evt_str()` maps event bits to strings, and `is_new_frame()` detects FLIP/EOW frame boundaries.

Control flow: KMS IRQ handler receives decoded chip events and calls `komeda_print_events()`. The function computes an event mask based on `mdev->err_verbosity`, rate-limits to the first relevant event per frame unless disabled, prints combined global/pipe event strings, and optionally dumps DRM atomic state on error/warning events.

State and persistence: uses static `en_print` as global rate-limit state across devices. `err_verbosity` is mutable through debugfs.

Dependencies/integration: depends on DRM printing/state dump and event definitions in `komeda_dev.h`.

Risks: static rate-limit state is not per-device. Event string buffer truncation is silent except bounded. Duplicate/incorrect event labels would mislead debugging. Test signals: IRQ event injection, toggling `err_verbosity`, multiple-device behavior, state-dump-on-event, and ensuring repeated errors are suppressed or printed according to settings.
