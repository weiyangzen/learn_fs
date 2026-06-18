## sources/distributed-fs/ceph-client/drivers/fpga/dfl-fme-mgr.c

Purpose: this FPGA manager driver programs DFL FME partial reconfiguration hardware. It is the manager used by FME FPGA regions created per AFU port.

Important APIs and functions: `struct fme_mgr_priv` stores PR MMIO base and last PR error bits. `fme_mgr_write_init()` requires `FPGA_MGR_PARTIAL_RECONFIG`, resets the PR engine, waits for reset ack and idle status, clears previous errors, and writes the target region ID. `fme_mgr_write()` asserts `PR_START`, polls credit, and writes 32-bit bitstream words into `FME_PR_DATA`. `fme_mgr_write_complete()` asserts `PR_COMPLETE`, waits for hardware to clear `PR_START`, checks errors, and returns success or `-EIO`. `fme_mgr_status()` maps PR error bits to FPGA manager status flags.

Control flow: probe receives MMIO through platform data from PR management or maps resource 0, reads compatibility ID registers into `fpga_compat_id`, and registers a full FPGA manager. Programming is credit-driven and uses a long microsecond timeout for reset, idle, credit, and completion.

State and persistence: software persists only the MMIO base and most recent PR error value. Hardware PR control/status/error registers carry operation state. The manager's compatibility ID is fixed at probe and shared with regions for bitstream compatibility checks.

Dependencies and integration: it depends on the FPGA manager framework, DFL FME PR platform data, non-atomic 64-bit IO helpers, and the region/bridge platform devices created by `dfl-fme-pr.c`.

Risks: bitstream size must be a multiple of four; smaller trailing fragments fail. Credit polling uses a simple delay counter rather than elapsed time. If `fme_mgr_pr_error_handle()` sees status clean, it does not read/clear error bits. The write path casts buffer to `u32 *`, so alignment matters. Region ID is taken from image info and must match the port.

Test signals: test missing partial flag, PR reset ack timeout, idle timeout, stale error clearing, invalid non-multiple-of-four image sizes, credit timeout, completion timeout, each PR error bit mapping, and compatibility ID propagation to regions.
