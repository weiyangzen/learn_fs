# sources/distributed-fs/ceph-client/drivers/nvmem/meson-mx-efuse.c

Purpose: Read-only NVMEM provider for older Amlogic Meson6/Meson8/Meson8b eFuse controllers.

Important APIs/types/functions: `struct meson_mx_efuse_platform_data` supplies name and word size; `meson_mx_efuse_hw_enable()`/`hw_disable()` gate clock and power; `meson_mx_efuse_read_addr()` programs byte address, starts auto-read, polls busy, and reads data; `meson_mx_efuse_read()` loops across requested words.

Control flow: probe chooses compatible-specific word size, maps MMIO, gets the `core` clock, and registers a 512-byte read-only OTP NVMEM. Reads power the block, enable auto-read, iterate address conversions, copy partial final words, disable auto-read, and power down.

State/persistence: hardware eFuse is persistent and read-only. Driver state holds base, clock, and embedded `nvmem_config`.

Dependencies/integration: OF compatibles `amlogic,meson6-efuse`, `amlogic,meson8-efuse`, and `amlogic,meson8b-efuse`; uses MMIO, clock framework, polling helpers, and legacy fixed OF cells.

Risks: timeouts return after logging the failing address. The read path must always balance power/clock disable; current flow does so after loop exit. Static size is fixed to 512 bytes regardless of SoC-specific exposed data.

Test signals: compatible-specific word-size behavior, unaligned/partial reads, timeout path from `AUTO_RD_BUSY`, clock enable failures, and fixed-cell consumers.
