# sources/distributed-fs/ceph-client/drivers/gpu/drm/sitronix/Makefile

Purpose: maps Sitronix Kconfig symbols to object files.

Important APIs/types/functions: no C API. It builds `st7571.o`, `st7571-i2c.o`, `st7571-spi.o`, `st7586.o`, `st7735r.o`, and `st7920.o` based on the matching `CONFIG_DRM_*` symbols.

Control flow: Kbuild includes each object in the DRM subtree when its config symbol is enabled.

State and persistence: no runtime state.

Dependencies and integration: must stay aligned with Kconfig symbol names and module import namespaces. The ST7571 bus objects depend on symbols exported by `st7571.o`.

Risks: any renamed source or Kconfig symbol will silently break module inclusion. ST7571 transport modules require the core object to be built.

Test signals: `make M=drivers/gpu/drm/sitronix` or full kernel builds with each symbol combination should verify object inclusion.
