<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_debugfs.c -->
## sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_debugfs.c

Purpose: exposes selected CryptoCell registers and the DMA coherency flag through debugfs for diagnostics. It creates a global `ccree` debugfs directory and per-device subdirectories.

Important APIs, types, and functions: `CC_DEBUG_REG()` maps register names to offsets. Static register sets include `ver_sig_regs`, `pid_cid_regs`, and `debug_regs`. Public functions are `cc_debugfs_global_init()`, `cc_debugfs_global_fini()`, `cc_debugfs_init()`, and `cc_debugfs_fini()`.

Control flow: module init calls global init to create `/sys/kernel/debug/ccree`. Device initialization calls `cc_debugfs_init()`, which allocates debugfs regset structures with devm memory, creates a per-platform-device directory, exposes a `regs` regset and `coherent` bool, then exposes either legacy signature/version registers or PID/CID registers depending on hardware revision. Teardown removes the per-device directory recursively, and module exit removes the global directory.

State and persistence behavior: `cc_debugfs_dir` is a global dentry pointer for module lifetime. Each `cc_drvdata` stores its per-device debugfs directory in `drvdata->dir`. Files are runtime-only debugfs entries and do not persist across unload or reboot.

Dependencies and integration points: depends on Linux debugfs, register-offset macros from `cc_host_regs` via `cc_driver.h`, and hardware revision/offset fields initialized in `cc_driver.c`. `cc_driver.c` owns call ordering around probe/remove and module init/exit.

Risks: debugfs register exposure is read-only but can still leak hardware state useful for diagnostics or attackers with debugfs access. The global `ver_sig_regs` offsets are mutable and shared, so multiple devices with different revisions could conflict. Failure to allocate the version regset is intentionally non-fatal, so missing debugfs version data should not be treated as probe failure.

Test signals: mount debugfs and verify per-device `regs`, `version`, and `coherent` files appear; test both <=712 and >712 register layouts; unload/reload the module and check cleanup; boot with `CONFIG_DEBUG_FS=n` to verify stub behavior from the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_debugfs.c -->
