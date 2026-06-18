# sources/distributed-fs/ceph-client/tools/testing/selftests/alsa/pcm-test.c

Purpose: kselftest that enumerates ALSA PCM devices and runs timing-based playback/capture tests using default and system-specific configurations.

Important APIs/types/functions: `struct card_data` and `struct pcm_data`; global `pcm_list`, `pcm_missing`, `default_pcm_config`, and `results_lock`; timestamp helpers; config parsing helpers `device_from_id()`, `missing_device()`, `missing_devices()`; discovery `find_pcms()`; core `test_pcm_time()`; `run_time_tests()`; per-card thread `card_thread()`; `main()`.

Control flow: loads `pcm-test.conf`, loads host-specific `conf.d`, discovers PCM devices/subdevices/streams, records configured-but-missing devices, computes kselftest plan, reports unmatched configs/missing PCMs, then spawns one thread per card to run default and system-specific time tests. Each time test opens `hw:card,device,subdevice`, applies configured access/format/rate/channel/period/buffer params, writes or reads two seconds of silence, drains, and checks elapsed time within 100 ms.

State and persistence: uses linked lists and libasound handles; no persistent writes. It reads config files and live ALSA/sysfs state.

Dependencies/integration: libasound PCM/control APIs, pthreads, kselftest, `alsa-local` helpers, `pcm-test.conf`, and optional per-host config.

Risks and test signals: can conflict with active audio. Timing checks can be flaky under heavy scheduler load. Source includes duplicated `if (err < 0)` and an apparent stray comment terminator in the system test result block; these are build/maintenance risks if not patched elsewhere.
