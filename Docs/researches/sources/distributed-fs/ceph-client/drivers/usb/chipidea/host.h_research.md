# sources/distributed-fs/ceph-client/drivers/usb/chipidea/host.h

Purpose: declares the ChipIdea host-role initialization, destruction, and EHCI driver setup hooks, with inline no-op or `-ENXIO` stubs when host support is disabled.

Important APIs/types/functions: declares `ci_hdrc_host_init`, `ci_hdrc_host_destroy`, and `ci_hdrc_host_driver_init` under `CONFIG_USB_CHIPIDEA_HOST`; otherwise provides fallback stubs.

Control flow: no runtime flow beyond stubs. The core can call host hooks regardless of Kconfig and receive a clean unsupported-role error.

State and persistence: no owned state; real host implementation populates `ci->roles[CI_ROLE_HOST]` and manages `ci->hcd`.

Dependencies and integration: included by `core.c` and `host.c`, coupling the core role setup to optional EHCI host support.

Risks: host-disabled builds rely on callers handling `-ENXIO`. Empty destroy/init-driver stubs must remain safe when called unconditionally by core init/unwind paths.

Test signals: build and probe host-disabled configurations, host-enabled module init, and error paths where host hardware is absent.
