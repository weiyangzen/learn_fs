# sources/distributed-fs/ceph-client/drivers/mmc/core/sd_ops.h Research

## sources/distributed-fs/ceph-client/drivers/mmc/core/sd_ops.h

### Purpose
`sd_ops.h` declares internal SD command helpers for the MMC core.

### Important APIs, Types, And Functions
It declares helpers for SD APP bus width, ACMD41 OCR negotiation, CMD8 interface checks, SD Express CMD8 probing, RCA assignment, SCR and SSR reads, APP_CMD, SDUC extension address, and UHS-II request preparation: `mmc_app_set_bus_width()`, `mmc_send_app_op_cond()`, `mmc_send_if_cond()`, `mmc_send_if_cond_pcie()`, `mmc_send_relative_addr()`, `mmc_app_send_scr()`, `mmc_app_sd_status()`, `mmc_app_cmd()`, `mmc_send_ext_addr()`, and `mmc_uhs2_prepare_cmd()`.

### Control Flow
There is no runtime control flow. The declarations let higher-level attach/setup code call the low-level command wrappers in `sd_ops.c` and `sd_uhs2.c`.

### State, Persistence, And Dependencies
No state is stored. The header depends on `linux/types.h` and opaque declarations for `mmc_card`, `mmc_host`, and `mmc_request`.

### Integration Points
Included by SD, SDIO, and UHS-II implementation files to keep SD command construction centralized.

### Risks
Because `mmc_uhs2_prepare_cmd()` is declared here but implemented in `sd_uhs2.c`, non-UHS-II builds must still satisfy link/config expectations. Any prototype drift can break several attach paths.

### Test Signals
Compile matrix coverage with SD, SDIO, SD Express, and UHS-II options validates this header's exported internal surface.
