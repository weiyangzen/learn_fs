# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/st/Makefile

Purpose: Vendor-level build glue for ST wireless drivers.

Important APIs and types: Adds the `cw1200/` subdirectory to `obj-y`/`obj-m` when `CONFIG_CW1200` is enabled.

Control flow: Kbuild descends into the CW1200 directory only for enabled core support. Bus modules are selected within that subdirectory.

State and persistence: No runtime state. Build state is controlled by kernel configuration symbols.

Dependencies and integration: Depends on the CW1200 subdirectory Makefile and parent wireless Makefile traversal.

Risks: If new ST drivers are added, this Makefile must be extended. Current file intentionally builds only CW1200.

Test signals: `make M=drivers/net/wireless/st` or full kernel builds should include `cw1200/` when `CONFIG_CW1200` is set.
