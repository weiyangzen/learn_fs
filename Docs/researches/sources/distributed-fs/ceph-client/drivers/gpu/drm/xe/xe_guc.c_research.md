# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc.c

## Purpose

`xe_guc.c` is the main lifecycle and command glue for the GuC microcontroller. It initializes firmware metadata and GuC subsystems, builds GuC boot parameters, uploads firmware, enables communication, handles reset/suspend/resume, provides MMIO and CT command helpers, manages optional GuC-to-GuC buffers, and exposes diagnostic printing and wedging behavior.

## Important APIs, Types, and Functions

- Initialization: `xe_guc_comm_init_early()`, `xe_guc_init_noalloc()`, `xe_guc_init()`, `xe_guc_init_post_hwconfig()`, `xe_guc_post_load_init()`.
- Firmware load: `xe_guc_min_load_for_hwconfig()`, `xe_guc_upload()`, `__xe_guc_upload()`, `guc_write_params()`, `guc_prepare_xfer()`, `guc_xfer_rsa()`, `guc_wait_ucode()`.
- Reset/power: `xe_guc_reset()`, `xe_guc_suspend()`, `xe_guc_softreset()`, `xe_guc_runtime_suspend()`, `xe_guc_runtime_resume()`, `xe_guc_sanitize()`, `xe_guc_declare_wedged()`.
- Communication: `xe_guc_enable_communication()`, `xe_guc_notify()`, `xe_guc_mmio_send_recv()`, `xe_guc_mmio_send()`, `xe_guc_self_cfg32()`, `xe_guc_self_cfg64()`, `xe_guc_irq_handler()`.
- Feature and setup helpers: `guc_ctl_*()` parameter builders, `xe_guc_opt_in_features_enable()`, G2G allocation/registration helpers, `xe_guc_using_main_gamctrl_queues()`, and `xe_guc_print_info()`.

## Control Flow

Early init selects the host interrupt register and initializes CT/relay. Normal PF init loads GuC firmware metadata, initializes log, capture, ADS, and CT, marks firmware loadable, registers managed cleanup, and writes minimal params. SR-IOV VF init follows a separate bootstrap/config-query path and initializes only the VF-relevant CT/submission pieces. The driver performs a minimal upload to read hwconfig, then post-hwconfig reallocates DGFX BOs to VRAM, initializes CT, submission, doorbells, PC/RC/activity, buffer cache, and ADS. Full upload populates ADS, optionally selects main GAMCTRL queues, writes params into soft scratch registers, programs transfer registers, supplies RSA data, DMA-loads ucode, and polls `GUC_STATUS` until ready or terminal failure.

## State and Persistence Behavior

Persistent GuC state lives in `struct xe_guc`: firmware object, params array, log/ADS/CT/submission/PC/RC/buffer-cache state, notify register, and optional G2G BO. Firmware status transitions through loadable, running, load fail, and sanitized states. Managed device actions clean up hardware state or VF state. Runtime suspend pauses submission, disables it, and disables CT; resume re-enables IRQ/CT/submission and unpauses.

## Dependencies and Integration Points

This file integrates nearly every GuC-facing subsystem: firmware loader, WOPCM, MMIO/forcewake, ADS, capture, CT, log, hwconfig, submission, DB manager, PC/RC, relay, page/memirq, SR-IOV PF/VF migration, GT reset, throttling, workarounds, and configfs. Hardware register definitions and GuC ABI headers define parameter, action, and status formats.

## Risks and Edge Cases

Boot parameter correctness is version/platform-sensitive. `xe_guc_mmio_send_recv()` must handle lost scratch registers during FLR, busy replies, retry replies, migration rejection, and protocol corruption. The minimal-load and full-load stages share state but have different ADS/submission expectations. G2G support is mostly dormant because `xe_guc_g2g_wanted()` returns false. Reset and suspend paths must avoid leaving CT/submission enabled against dead firmware.

## Test Signals

KUnit coverage exists for G2G under `CONFIG_DRM_XE_KUNIT_TEST`. Additional signals include fault injection on init/upload paths, mocked MMIO send responses for success/busy/retry/failure/lost-FLR/protocol cases, firmware load status decoding tests, suspend/resume sequencing tests, SR-IOV VF bootstrap/migration paths, and integration runs verifying GuC status/debugfs output after load and reset.
