# sources/distributed-fs/ceph-client/drivers/staging/sm750fb/Kconfig

Purpose: declares the kernel configuration option for the Silicon Motion SM750 framebuffer staging driver.

Important APIs/types/functions: `config FB_SM750` is a tristate option named "Silicon Motion SM750 framebuffer support". It depends on `FB`, `PCI`, and `HAS_IOPORT`, and selects framebuffer helper operations `FB_MODE_HELPERS`, `FB_CFB_FILLRECT`, `FB_CFB_COPYAREA`, and `FB_CFB_IMAGEBLIT`.

Control flow: no runtime flow; Kconfig controls whether `CONFIG_FB_SM750` is absent, built-in, or module. The help text identifies module name `sm750fb`.

State and persistence: selected config persists in the kernel build configuration and determines object inclusion by the Makefile.

Dependencies and integration: integrates with the staging drivers Kconfig tree, PCI framebuffer infrastructure, I/O port availability, and cfb helper implementations.

Risks: selecting cfb helpers pulls in software framebuffer operations and assumes the legacy fbdev subsystem. `HAS_IOPORT` is required because SM750LE mode setup uses x86-style VGA I/O paths in some code paths.

Test signals: build coverage for `CONFIG_FB_SM750=m` and `=y`, dependency resolution without `PCI` or `HAS_IOPORT`, and module name/load tests.
