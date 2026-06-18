## sources/distributed-fs/ceph-client/drivers/fpga/dfl-fme-pr.c

Purpose: this file implements DFL FME partial-reconfiguration orchestration. It creates child FPGA manager, bridge, and region devices for each implemented port and exposes the `DFL_FPGA_FME_PORT_PR` ioctl to program a port region from a userspace buffer.

Important APIs and functions: `fme_pr()` copies a `struct dfl_fpga_fme_port_pr`, validates args and port ID, aligns buffer length to 4 bytes, copies the bitstream with `vmalloc()`, creates `fpga_image_info`, finds the target `fpga_region`, sets partial-reconfig flags and region ID, calls `fpga_region_program_fpga()`, and releases bridge references afterward. `pr_mgmt_init()` creates one FME manager plus bridge/region platform devices for implemented ports based on `FME_HDR_CAP` and port offset registers. Destroy helpers unregister child devices and maintain FME lists.

Control flow: PR management feature init initializes region and bridge lists, creates the manager from the PR feature MMIO, iterates implemented ports, creates bridge devices tied to DFL port IDs, and creates matching FPGA region devices. The ioctl path later uses those lists to find the target region and invokes the generic FPGA region programming flow, which disables bridges, calls the FME manager, and re-enables bridges.

State and persistence: `struct dfl_fme` holds child manager, bridge list, and region list. Each `struct dfl_fme_region` maps a port ID to a region platform device. During an ioctl, the image buffer and info are transient; `region->info` is replaced and later the local buffer is freed after programming returns.

Dependencies and integration: it depends on FPGA manager/bridge/region frameworks, DFL FME header registers, FME child drivers (`dfl-fme-mgr`, `dfl-fme-br`, `dfl-fme-region`), and userspace DFL ioctl ABI.

Risks: the aligned `vmalloc(length)` buffer is not explicitly zeroed beyond `buffer_size`, so padded bytes may contain uninitialized data, although comments state hardware ignores padding. The code frees `buf` after `fpga_region_program_fpga()` while assigning it into `region->info`; this relies on programming being synchronous and no later consumer using the stale pointer. Holding `fdata->lock` across `fpga_region_program_fpga()` can serialize PR but may interact with bridge operations that call back into DFL port ops. Region platform data includes `region_id` in the header but creation does not set it.

Test signals: test invalid argsz/flags, out-of-range port IDs, missing region, copy-from-user failures, non-multiple-of-four buffer sizes, manager/bridge/region creation unwinds, implemented versus unimplemented port offsets, PR success path bridge release, and concurrent PR ioctl serialization.
