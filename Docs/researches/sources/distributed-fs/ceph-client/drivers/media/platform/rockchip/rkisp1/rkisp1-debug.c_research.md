# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkisp1/rkisp1-debug.c

Purpose: optional debugfs support for RKISP1. It exposes debug counters, sampled input status, and selected live/shadow register dumps when `CONFIG_DEBUG_FS` is enabled.

Important APIs/types/functions: exports `rkisp1_debug_init()` and `rkisp1_debug_cleanup()`. Internal `struct rkisp1_debug_register` describes register dumps, `rkisp1_debug_dump_regs()` reads registers only if runtime PM says the device is active, and show functions dump core, ISP, resizer, and MI mainpath registers. `rkisp1_debug_input_status_show()` samples ISP input flags 10,000 times with 1 us delay and reports VSYNC/HSYNC/data distribution.

Control flow: platform probe calls `rkisp1_debug_init()` after notifier/entity setup; remove calls cleanup. debugfs files are read on demand. Register dump reads call `pm_runtime_get_if_in_use()` and return `-ENODATA` if the device is suspended/inactive.

State and persistence: debug counters live in `struct rkisp1_debug` and are incremented by ISR/stream paths; debugfs directory dentries are stored for cleanup. No durable persistence and counters reset when driver reloads.

Dependencies/integration: depends on debugfs, seq_file, runtime PM, RKISP1 register definitions, and counters maintained by `rkisp1-isp.c`, `rkisp1-csi.c`, and `rkisp1-capture.c`.

Risks: debugfs reads intentionally avoid waking the device, so register dumps may be unavailable when idle. The input status sampler busy-waits for about 10 ms and should not be used as a high-frequency polling interface. Register lists must be kept up to date with hardware/register changes.

Test signals: with `CONFIG_DEBUG_FS`, verify directory creation/removal, counter increments under frame drops/errors/timeouts, register dumps while streaming, `-ENODATA` while inactive, and input status output during sensor activity.
