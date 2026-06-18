# sources/distributed-fs/ceph-client/drivers/reset/amlogic/Makefile

Purpose: maps Amlogic reset Kconfig symbols to Meson reset objects.

Important APIs/types/functions: builds `reset-meson.o`, `reset-meson-aux.o`, `reset-meson-common.o`, and `reset-meson-audio-arb.o` under their corresponding `CONFIG_RESET_MESON*` symbols.

Control flow: build-time only through Kbuild object selection.

State and persistence: no runtime state; object inclusion follows `.config`.

Dependencies and integration: the common object must be linked whenever platform or auxiliary Meson drivers are enabled because it exports common ops and registration helpers.

Risks and test signals: namespace export/import mismatches or missing common object entries cause link failures. Build test each symbol as built-in and module where supported.
