# sources/distributed-fs/ceph-client/drivers/platform/arm64/Makefile

Purpose: kbuild mapping from ARM64 EC Kconfig symbols to object files.

Important APIs, types, and functions: maps `CONFIG_EC_ACER_ASPIRE1` to `acer-aspire1-ec.o`, `CONFIG_EC_HUAWEI_GAOKUN` to `huawei-gaokun-ec.o`, `CONFIG_EC_LENOVO_YOGA_C630` to `lenovo-yoga-c630.o`, and `CONFIG_EC_LENOVO_THINKPAD_T14S` to `lenovo-thinkpad-t14s.o`.

Control flow: when symbols are `y`, objects are linked built-in; when `m`, modules are generated. No composite objects are defined here.

State and persistence: build-only; no runtime state.

Dependencies and integration points: must align exactly with `drivers/platform/arm64/Kconfig` symbol names and source filenames.

Risks and edge cases: filename-symbol drift prevents selected drivers from building. The comment scopes this directory to EC-like devices, which is a maintenance boundary rather than an enforced rule.

Test signals: `make M=drivers/platform/arm64` or whole-kernel compile with each symbol as module.
