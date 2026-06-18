# sources/distributed-fs/ceph-client/tools/testing/selftests/media_tests/video_device_test.c

Purpose: V4L2 device stress tool that verifies priority ioctl behavior and loops over capability/tuner ioctls during manual device removal/unbind.

Important APIs/types/functions: uses `VIDIOC_G_PRIORITY`, `VIDIOC_S_PRIORITY`, `VIDIOC_QUERYCAP`, `VIDIOC_G_TUNER`, `struct v4l2_capability`, and `struct v4l2_tuner`.

Control flow: parses `-d /dev/videoX`, opens the device, runs `priority_test()` to change priority and restore the old value, prints pass/fail, then `loop_test()` runs random-count iterations issuing querycap and tuner ioctls every ten seconds.

State and persistence: temporarily changes V4L2 file priority and restores it; holds device FD during external hardware churn.

Dependencies and integration points: V4L2 device node and driver supporting the tested ioctls; intended to be paired with dmesg/KASAN observation.

Risks: no root check but some devices require permissions. Random loop length can be long. `VIDIOC_G_TUNER` may be unsupported for non-tuner devices and is treated diagnostically.

Test signals: priority round-trip pass/fail plus absence of kernel errors while ioctls run during removal.
