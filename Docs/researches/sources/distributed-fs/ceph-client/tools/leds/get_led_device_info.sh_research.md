<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/leds/get_led_device_info.sh -->
# sources/distributed-fs/ceph-client/tools/leds/get_led_device_info.sh

Purpose: this shell script inspects an LED class device in sysfs, reports hardware details, and validates the LED class device name against Linux LED color/function definitions.

Important APIs/functions: it accepts `LED_CDEV_PATH` and optionally `LED_COMMON_DEFS_PATH`; otherwise it derives the kernel top and uses `include/dt-bindings/leds/common.h`. It probes `brightness`, bus type via `device/subsystem`, USB ancestry, OF compatible strings, input devices, drivers, vendor/product/manufacturer files, and optional Wi-Fi phy names. Helper functions `print_msg_ok` and `print_msg_failed` format validation rows.

Control flow: after argument and path validation, the script classifies the LED as USB, input, OF gpio/pwm/compatible, or unknown. It prints hardware fields, splits the LED device basename on `:`, maps one/two/three-section names to devicename/color/function, derives expected device names from input or wifi phy, checks redundant/unknown devicenames, and looks up color/function definitions in the common header.

State and persistence: it reads sysfs and the definitions header only; no system state is changed. It exits nonzero on invalid paths, unknown types, malformed names, or failed hard checks.

Dependencies/integration: depends on POSIX shell utilities (`realpath`, `dirname`, `awk`, `sed`, `grep`, `cut`, `readlink`, `ls`, `cat`, `tr`) and Linux LED sysfs layout.

Risks and test signals: risks include unquoted variables in tests/cd/cat paths, fragile USB path regexes, binary OF compatible contents, grep pattern false positives, and assumptions about input/driver paths. Test LED names with one/two/three colon sections, USB Wi-Fi LEDs, input LEDs, gpio/pwm OF LEDs, missing definitions, spaces/special chars in paths, and unknown bus types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/leds/get_led_device_info.sh -->
