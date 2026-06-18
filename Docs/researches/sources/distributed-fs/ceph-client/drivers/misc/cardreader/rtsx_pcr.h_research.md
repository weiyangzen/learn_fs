# sources/distributed-fs/ceph-client/drivers/misc/cardreader/rtsx_pcr.h

Purpose: declares shared private constants, vendor-setting decode macros, chip initializer prototypes, pull-control table macro, and generic helper prototypes for the Realtek PCI cardreader driver family.

Important APIs, types, and functions: prototypes cover low-level PHY access (`__rtsx_pci_write_phy_register()`, `__rtsx_pci_read_phy_register()`), every chip initializer (`rts5209_init_params()` through `rts5264_init_params()`), LTR/L1/OCP helpers, and OOBS polling helpers. `map_sd_drive()` converts a drive-strength index into hardware drive selection. `set_pull_ctrl_tables()` assigns SD/MS pull-control table pointers in `struct rtsx_pcr`.

Control flow: the header determines compile-time call targets used by `rtsx_pcr.c` chip dispatch and by individual chip files. The decode macros shape vendor-setting parsing in older chip implementations outside this work item and the helper prototypes shape generic OCP/PM dispatch.

State and persistence: constants define min/max SSC divider limits, default LTR latencies, default L1 snooze delay, command timeout, SSC stable delay, and OCP threshold defaults. Vendor-setting macros map persistent PCI/efuse config fields into runtime `pcr` policy such as MMC support, RTD3, UHS-II RTD3, ASPM, drive strengths, and reversed socket/CD/WP wiring.

Dependencies and integration points: included by common and chip-specific Realtek PCI cardreader sources. It depends on `linux/rtsx_pci.h` for `struct rtsx_pcr` and register/flag definitions. It is the private coordination point between common driver lifecycle code and chip implementation files.

Risks: macro-only bitfield parsing has no type safety and silently accepts unexpected register layouts. Default latency/threshold constants affect power/performance behavior across multiple chips. Because this is a shared private header, changing generic macros can regress chip files not in this subset.

Test signals: all Realtek cardreader objects should compile after changes. Runtime validation requires checking debug logs for decoded vendor settings and confirming each supported PCI ID still selects the intended initializer and OCP/LTR defaults.
