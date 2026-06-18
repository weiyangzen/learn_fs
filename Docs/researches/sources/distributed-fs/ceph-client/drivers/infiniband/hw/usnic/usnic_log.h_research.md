# sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_log.h

Purpose: lightweight logging macros and log-level declarations for usNIC.

Important APIs/data: declares external `usnic_log_lvl`, level constants NONE/ERR/INFO/DBG, and macros `usnic_printk`, `usnic_dbg`, `usnic_info`, and `usnic_err`.

Control flow: call sites emit messages only when the module parameter `usnic_log_lvl` is high enough. Prefixes include driver name, function, and line number.

State and persistence: the mutable log level is defined in `usnic_ib_main.c` and exposed as a module parameter.

Dependencies and integration: includes `usnic.h` for `DRV_NAME`; used by nearly every usNIC implementation file.

Risks: macros use `printk` directly and can produce noisy logs at debug level. The macro formatting is old-style variadic GNU C and should be kept build-compatible. Line-number prefixes change with edits, which can affect log matching.

Test signals: module parameter read/write, logs at each level, and build coverage with all macro call patterns.
