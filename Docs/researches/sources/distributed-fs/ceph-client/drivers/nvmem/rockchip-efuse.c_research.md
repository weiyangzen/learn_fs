# sources/distributed-fs/ceph-client/drivers/nvmem/rockchip-efuse.c

Purpose: Read-only OTP NVMEM provider for older Rockchip eFuse controllers.

Important APIs/types/functions: `struct rockchip_efuse_chip` holds device, base, and `pclk_efuse`. `rockchip_rk3288_efuse_read()`, `rockchip_rk3328_efuse_read()`, and `rockchip_rk3399_efuse_read()` implement SoC-family-specific register sequences. Match data is a function pointer used as `econfig.reg_read`.

Control flow: probe resolves match-data read function, maps MMIO, gets clock, chooses size from `rockchip,efuse-size` or resource size, and registers byte-granular read-only NVMEM. Runtime reads enable the clock, execute the family-specific address/strobe/auto-read flow, copy aligned temporary data as needed, put hardware in standby, and disable the clock.

State/persistence: eFuse data is persistent and read-only. Driver state is MMIO/clock only; no cache.

Dependencies/integration: supports deprecated generic and SoC-specific compatibles from RK3066A through RK3399; uses clock framework, MMIO, OF property sizing, and legacy fixed cells.

Risks: RK3328 offsets are shifted by the secure-region size, exposing only non-secure bytes. Static global `econfig` is mutated per probe. Polling/interrupt status handling differs by SoC and needs hardware-specific coverage.

Test signals: all compatible function selections, RK3328 secure offset translation, partial reads over 4-byte words, missing `rockchip,efuse-size`, and clock enable failure.
