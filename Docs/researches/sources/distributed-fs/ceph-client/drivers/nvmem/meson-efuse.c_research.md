# sources/distributed-fs/ceph-client/drivers/nvmem/meson-efuse.c

Purpose: Amlogic Meson GX eFuse NVMEM provider mediated through secure monitor firmware.

Important APIs/types/functions: `meson_efuse_read()` and `meson_efuse_write()` call `meson_sm_call_read()`/`meson_sm_call_write()` with `SM_EFUSE_READ` and `SM_EFUSE_WRITE`. Probe resolves the `secure-monitor` phandle, obtains `struct meson_sm_firmware`, enables the eFuse gate clock, asks firmware for `SM_EFUSE_USER_MAX`, and registers byte-granular NVMEM.

Control flow: probe defers until secure monitor firmware is available, then computes the size from firmware and exposes read/write callbacks. Runtime NVMEM operations are direct firmware calls that return 0 on nonnegative secure monitor result.

State/persistence: eFuse contents persist in silicon; the driver stores only firmware pointer/config. Writes are permanent if firmware allows them.

Dependencies/integration: platform driver for `amlogic,meson-gxbb-efuse`; depends on Meson secure monitor firmware and a clock gate.

Risks: write availability is exposed to NVMEM consumers, so policy is entirely dependent on firmware and NVMEM permissions. Probe fails if firmware cannot return the user size. Secure monitor call argument semantics are opaque to this driver.

Test signals: secure monitor present/deferred/failing paths, size query failure, read/write firmware errors, and fixed-cell reads through legacy OF cells.
