# sources/distributed-fs/ceph-client/tools/testing/selftests/media_tests/media_dev_allocator.sh

Purpose: manual script to exercise media device allocator behavior while unbinding and rebinding related media/audio USB drivers.

Important APIs/types/functions: uses `/sys/bus/usb/drivers/$1` and `$2`, discovers devices via `ls -d *-*` and `*-*.1`, writes to driver `unbind`/`bind`, and inspects `/dev/media*`.

Control flow: accepts media driver and audio driver names, unbinds media then audio, checks media node presence/deletion, rebinds both, then runs another interleaved unbind/bind sequence.

State and persistence: mutates live USB driver binding and device nodes. Uses sleeps to let device state settle.

Dependencies and integration points: specific USB hardware, driver names, root, sysfs, media device allocator.

Risks: no argument validation, no cleanup trap, and `cd`/glob failures can affect the wrong path or abort unpredictably. It is intended for supervised hardware testing.

Test signals: human-readable `ls -l /dev/media*` observations; no formal pass/fail exit checks.
