# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_lightbar.c

Purpose: sysfs interface exposing Chromebook Pixel-style EC lightbar control to userspace.

Important APIs, types, and functions: global knobs include `lb_interval_jiffies`, `userspace_control`, `has_manual_suspend`, and `lb_version`. `alloc_lightbar_cmd_msg()` creates EC lightbar command buffers. `get_lightbar_version()` detects support and flags. Sysfs handlers expose `interval_msec`, `num_segments`, `version`, write-only `brightness`, `led_rgb`, `sequence`, `program`, and `userspace_control`. Suspend/resume send lightbar suspend/resume EC commands unless userspace has control.

Control flow: probe only binds to the main `cros_ec` device name, verifies lightbar support, attempts to enable manual suspend control, and creates a `lightbar` sysfs group under the EC class device. Each sysfs operation throttles through `lb_throttle()` to limit command rate, builds an `EC_CMD_LIGHTBAR_CMD`, and sends it via `cros_ec_cmd_xfer_status()`. `program_store()` sends either one legacy program payload or chunks for v3 extended program writes. Remove removes the sysfs group and releases manual suspend control.

State and persistence: module-global state controls throttle interval, userspace ownership, manual-suspend capability, and detected version. These are not per EC instance. Lightbar sequence/brightness/program state persists in EC firmware/hardware. `userspace_control` affects PM behavior only.

Dependencies and integration points: platform `cros-ec-dev`, EC lightbar host commands, sysfs attribute groups, PM ops, and Chrome EC command offsets. It intentionally excludes `cros_pd`.

Risks and edge cases: globals make multiple EC/lightbar instances unsafe. Throttling sleeps in sysfs write/read context and can be interrupted. `led_rgb_store()` parses decimal/hex-style integers with `sscanf("%i")` and requires groups of four. Program sizing depends on EC max request and protocol version. Manual suspend detection treats `-EINVAL` as unsupported but other errors as supported failure path.

Test signals: sysfs group appears only on devices with lightbar support, version/segment reads, sequence by name and number, RGB writes in groups of four, program upload for v0/v3 devices, throttle behavior, userspace-control PM suppression, and cleanup restoring EC control.
