# sources/distributed-fs/ceph-client/drivers/mmc/core/sd.h Research

## sources/distributed-fs/ceph-client/drivers/mmc/core/sd.h

### Purpose
`sd.h` is the internal SD memory-card contract between MMC core files. It exposes SD card type metadata and the core SD identification/setup helpers without leaking implementation details from `sd.c`.

### Important APIs, Types, And Functions
It declares `extern const struct device_type sd_type`, forward declares `struct mmc_host` and `struct mmc_card`, and declares `mmc_sd_get_cid()`, `mmc_sd_get_csd()`, `mmc_decode_scr()`, `mmc_sd_get_ro()`, `mmc_decode_cid()`, `mmc_sd_setup_card()`, `mmc_sd_get_max_clock()`, and `mmc_sd_switch_hs()`.

### Control Flow
The header has no runtime logic. `sd.c`, SDIO combo handling, and UHS-II legacy initialization include it to decode/register memory-card portions and to reuse high-speed/card setup operations.

### State, Persistence, And Dependencies
No state is stored here. It depends only on `linux/types.h` and opaque MMC card/host declarations, keeping the compile-time interface narrow.

### Integration Points
`sdio.c` and `sd_uhs2.c` use this header for combo-card memory setup, CID/CSD/SCR decoding, high-speed switching, and max-clock calculation. `sd_type` links SD card allocations to the SD sysfs attribute group.

### Risks
Any signature change affects several MMC core paths. The header intentionally omits attach and PM functions, so callers must continue using bus attach APIs rather than bypassing SD initialization.

### Test Signals
Compile coverage for SD-only, SDIO-combo, and UHS-II configurations validates the declarations. Runtime coverage is inherited from the implementation users.
