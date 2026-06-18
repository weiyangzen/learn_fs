# sources/distributed-fs/ceph-client/tools/testing/selftests/alsa/pcm-test.conf

Purpose: default ALSA PCM timing-test matrix consumed by `pcm-test`.

Important APIs/types/functions: declares `pcm.test.time1` through `time7` with descriptions, primary `S16_LE` format, alternate `S32_LE`, rates from 8 kHz to 96 kHz, channels, period sizes, and buffer sizes.

Control flow: `pcm-test.c` iterates the `pcm.test` compound and runs each block as a `time` test unless overridden.

State and persistence: declarative config only.

Dependencies/integration: parsed by libasound config APIs through `conf_load_from_file()`.

Risks and test signals: `time6` description says 6 channel but `channels 2`, which may be an intentional label error or stale config. Unsupported formats/rates become skips/failures depending on default versus system-specific class.
