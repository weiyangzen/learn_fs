# sources/distributed-fs/ceph-client/tools/testing/selftests/alsa/conf.d/Lenovo_ThinkPad_P1_Gen2.conf

Purpose: host-specific ALSA selftest configuration for Lenovo ThinkPad P1 Gen2 HDA audio.

Important APIs/types/functions: defines a global `sysfs` match against `class/dmi/id/product_sku`; defines `card.hda` with card-level sysfs matches for subsystem device/vendor; configures `pcm.0.0` PLAYBACK tests `time1`, `time2`, `time3` and a CAPTURE presence block.

Control flow: loaded by `conf.c` only if the global sysfs regex matches. If card sysfs matches, PCM tests use the card-specific `pcm.*` blocks for required devices and system-specific timing tests.

State and persistence: declarative config only; no runtime writes.

Dependencies/integration: consumed by ALSA `conf_load()`, `missing_devices()`, and `run_time_tests()`.

Risks and test signals: regexes are hardware-specific and stale DMI/subsystem strings would silently skip the config. Uncommented missing-device blocks can convert absent PCMs into explicit failures.
