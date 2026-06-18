# sources/distributed-fs/orangefs/src/io/dev/module.mk.in

Purpose: build fragment for the device bridge module.

Important content: sets `DIR := src/io/dev`, adds `$(DIR)/pint-dev.c` to `LIBSRC`, and gives `pint-dev.c` an include path for `src/kernel/linux-2.6`.

Integration: makes the user-space device implementation part of the OrangeFS library build and supplies kernel-protocol headers used by `pint-dev.c`.

Risks/test signals: stale kernel include path naming (`linux-2.6`) may matter on modern build systems even if retained for compatibility. Build tests should confirm the generated makefiles compile `pint-dev.c` with the expected kernel helper headers.
