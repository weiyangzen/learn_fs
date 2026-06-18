<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/leds/Makefile -->
# sources/distributed-fs/ceph-client/tools/leds/Makefile

Purpose: this Makefile builds LED userspace tools `uledmon` and `led_hw_brightness_mon`.

Important APIs/targets: `CFLAGS = -Wall -Wextra -g -I../../include/uapi`; default target builds both tools using a generic `%: %.c` rule; `clean` removes both executables; `.PHONY` marks `all` and `clean`.

Control flow: invoking `make` compiles each C file into a same-name executable with the configured compiler and UAPI include path.

State and persistence: generated executables are stored in the tools/leds directory.

Dependencies/integration: depends on a C compiler and local UAPI headers. The directory also contains the shell validator researched separately.

Risks and test signals: risks include no install target and debug flags in default CFLAGS. Test `make`, warning-free builds under `-Wall -Wextra`, and `make clean`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/leds/Makefile -->
