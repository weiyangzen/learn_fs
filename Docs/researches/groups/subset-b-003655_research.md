# subset-b-003655 research

Grouped research for Qualcomm MSM HDMI HDCP/HPD/I2C/PHY/PLL support and core MSM DRM atomic, debugfs, driver, framebuffer, fence, GEM, and PRIME files.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/hdmi/hdmi_hdcp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/hdmi/hdmi_hdcp.c

## Purpose
Implements HDCP 1.x authentication for the MSM HDMI bridge. It drives the HDMI HDCP cipher, exchanges authentication data with the sink over DDC, validates local and remote KSVs, handles repeaters, and reauthenticates after HDCP link failures.

## Important APIs, types, and functions
- `struct hdmi_hdcp_ctrl` stores HDMI backpointer, retry counters, secure-world write mode, HDCP state, auth/reauth work items, wait events, AKSV/BKSV, repeater topology, and KSV FIFO.
- `msm_hdmi_hdcp_init()`, `msm_hdmi_hdcp_destroy()`, `msm_hdmi_hdcp_on()`, `msm_hdmi_hdcp_off()`, and `msm_hdmi_hdcp_irq()` are the integration surface used by the HDMI driver.
- DDC helpers `msm_hdmi_ddc_read()` and `msm_hdmi_ddc_write()` access HDCP receiver offsets at slave address `0x74`.
- Secure register writes go through `msm_hdmi_hdcp_scm_wr()` when `qcom_scm_hdcp_available()` is true, otherwise normal MMIO writes are used.
- Authentication phases are split across `msm_hdmi_hdcp_auth_prepare()`, part-1 key/R0 helpers, and part-2 repeater KSV/SHA helpers.

## Control flow
`msm_hdmi_hdcp_on()` clears encryption, resets auth events, marks the state authenticating, and queues `hdcp_auth_work`. The worker validates AKSV from QFPROM, switches DDC arbitration to software, writes AKSV/entropy, enables the HDCP block, clears stale DDC failures, waits for keys and An, reads BCAPS, sends An/AKSV, reads BKSV, enables HDCP interrupts, reads R0 prime after the required delay, and waits for the hardware result interrupt. Receiver-only sinks complete after part 1. Repeaters proceed to poll BCAPS READY, read BSTATUS, reject excessive depth/device counts, read the KSV FIFO and V prime hash values, reset the SHA engine, feed KSV bytes to the hardware in 64-byte chunks, and wait for V match.

Interrupt handling acknowledges success/failure bits under `reg_lock`. Auth success wakes the auth worker. Auth failure during an authenticated session queues reauth; failure during authentication wakes the worker to inspect status. Reauth temporarily disables HPD and HDCP interrupts, deauthenticates the link, waits for the DDC engine to settle, disables encryption, reenables HPD, and retries up to `AUTH_RETRIES_TIME`.

## State and persistence
State is held in `hdmi->hdcp_ctrl` and the workqueue while the HDMI device exists. The state machine transitions through no-AKSV, inactive, authenticating, authenticated, and failed. AKSV is cached after QFPROM validation. Hardware state persists in HDMI HDCP, DDC, HPD, SHA, and encryption registers until reset or power loss. Sink-side HDCP registers are written over DDC during each authentication.

## Dependencies and integration points
Depends on `hdmi.h` register helpers, the HDMI I2C/DDC adapter, QFPROM reads, Qualcomm SCM HDCP requests, Linux workqueues/waitqueues, and `hdmi->reg_lock`. It integrates with HDMI IRQ dispatch, bridge enable/disable paths, and the shared HDMI workqueue.

## Risks
Authentication is timing-sensitive and has several long polling loops. The DDC cleanup loop appears easy to misread because it breaks when hardware is not ready, so regressions around DDC recovery are likely. Secure-world register writes must use physical offsets correctly or HDCP programming fails. `ksv_list` size assumes the HDCP 1.x maximum of 127 downstream devices; incorrect BSTATUS handling can overrun protocol expectations. Work cancellation and HPD toggling must remain ordered or reauth/off can race with IRQ wakeups.

## Test signals
Useful signals are `AUTH_SUCCESS_INT`/`AUTH_FAIL_INT` logs, LINK0 status dumps, AKSV/BKSV hweight validation failures, DDC timeout/NACK logs, R0/V match failures, and retry exhaustion. Tests should cover no-QFPROM systems, receiver and repeater sinks, DDC failure recovery, hot-unplug during auth, reauth after link failure, and secure-world versus direct-MMIO paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/hdmi/hdmi_hdcp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/hdmi/hdmi_hpd.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/hdmi/hdmi_hpd.c

## Purpose
Provides HDMI hot-plug-detect control for MSM HDMI bridges: PHY reset during HPD setup, HPD interrupt enable/disable, IRQ processing, and connector detect using HPD registers and optional GPIO.

## Important APIs, types, and functions
- `msm_hdmi_hpd_enable()` powers the HDMI block, resets the PHY, enables HPD interrupts, and toggles the HPD circuit.
- `msm_hdmi_hpd_disable()` disables HPD interrupts, updates `hpd_enabled`, restores HDMI mode according to `power_on`, and drops runtime PM.
- `msm_hdmi_hpd_irq()` acknowledges HPD interrupt status, flips connect/disconnect interrupt polarity, and queues bridge HPD work.
- `msm_hdmi_bridge_detect()` reports connector status using `detect_reg()` and optional `detect_gpio()`.
- `msm_hdmi_phy_reset()` toggles software reset bits according to active-low/high polarity bits in `REG_HDMI_PHY_CTRL`.

## Control flow
HPD enable optionally drives the HPD GPIO high, resumes runtime PM, sets HDMI into detect mode under `state_mutex`, resets the PHY, marks HPD enabled, programs the reference timer and interrupt control, then toggles `HDMI_HPD_CTRL_ENABLE` under `reg_lock` to force a fresh sense. IRQ processing reads status/control, ignores disabled or unrelated interrupts, acknowledges the current interrupt, reprograms the next polarity based on cable state, and queues the bridge hotplug work. Detection retries up to 20 times for GPIO and register agreement, but trusts GPIO if they disagree.

## State and persistence
Persistent state is `hdmi->hpd_enabled`, `hdmi->power_on`, GPIO output state, runtime PM usage, and HPD/PHY controller registers. IRQ polarity persists in `REG_HDMI_HPD_INT_CTRL` until the next event. Detect reads do not cache connector state.

## Dependencies and integration points
Depends on DRM bridge callbacks, runtime PM, GPIO descriptors, HDMI register helpers, `hdmi->state_mutex`, `hdmi->reg_lock`, and `hdmi_bridge->hpd_work`. It is called from HDMI bridge HPD ops and connector detect paths.

## Risks
Detection can be delayed by the 20x10 ms retry loop. Runtime PM error paths call `pm_runtime_put()` even after failed resume in `detect_reg()`, so PM accounting assumptions matter. Register/GPIO disagreement is intentionally resolved in favor of GPIO, which can hide hardware HPD register issues. PHY reset polarity is hardware-specific.

## Test signals
Check hotplug connect/disconnect events, HPD interrupt status/control logs, detect behavior with and without HPD GPIO, runtime suspend/resume balance, and HDMI mode restoration after disabling HPD.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/hdmi/hdmi_hpd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/hdmi/hdmi_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/hdmi/hdmi_i2c.c

## Purpose
Implements the HDMI DDC I2C adapter used for EDID and HDCP DDC transactions through MSM HDMI controller registers.

## Important APIs, types, and functions
- `struct hdmi_i2c_adapter` wraps `struct i2c_adapter`, an HDMI pointer, SW_DONE latch, and waitqueue.
- `msm_hdmi_i2c_init()` creates/registers the adapter; `msm_hdmi_i2c_destroy()` unregisters and frees it.
- `msm_hdmi_i2c_xfer()` programs up to four hardware transactions and waits for SW_DONE.
- `msm_hdmi_i2c_irq()` wakes blocked transfers when the DDC interrupt says software transfer is done.
- `init_ddc()`, `ddc_clear_irq()`, and `sw_done()` initialize and service controller status.

## Control flow
Transfers are capped at `MAX_TRANSACTIONS`. The driver resumes HDMI runtime PM, soft-resets DDC state, clears stale interrupts, writes address/data bytes into `REG_HDMI_DDC_DATA`, programs each `REG_HDMI_I2C_TRANSACTION(i)` with count, direction, start, and final stop bits, triggers `HDMI_DDC_CTRL_GO`, and waits up to `HZ/4` for `ddc_event`. It then checks NACK bits per transaction and reads back data for read messages by programming the DDC data index and discarding the first returned byte.

## State and persistence
Runtime state is the adapter object and `sw_done` latch. Hardware DDC speed, timeout, reference timer, transaction registers, data FIFO/index, SW status, HW status, and interrupt control registers are reinitialized for each transfer. No EDID cache is stored here.

## Dependencies and integration points
Depends on Linux I2C core, runtime PM, HDMI register definitions, and HDMI IRQ dispatch. HDCP code uses this adapter through normal `i2c_transfer()`, and DRM connector probing uses it for EDID.

## Risks
Only four I2C messages are supported per transfer; callers with longer compound transfers are truncated by `min()`. Timeout and NACK handling returns the number of completed messages for partial success, so callers must interpret I2C semantics correctly. The code warns if HDMI CTRL is not enabled but still proceeds. DDC FIFO indexing is sensitive to off-by-one behavior.

## Test signals
Signals include DDC timeout warnings with SW/HW/int status, EDID read success, HDCP DDC reads/writes, NACK handling, interrupt wakeups, runtime PM balance, and behavior when HDMI is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/hdmi/hdmi_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/hdmi/hdmi_phy.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/hdmi/hdmi_phy.c

## Purpose
Provides the platform driver and common resource management for MSM HDMI PHY instances, dispatching to SoC-specific PHY/PLL implementations.

## Important APIs, types, and functions
- `msm_hdmi_phy_resource_init()` obtains configured regulators and clocks.
- `msm_hdmi_phy_resource_enable()` and `msm_hdmi_phy_resource_disable()` handle runtime PM, regulators, and clocks.
- `msm_hdmi_phy_powerup()` and `msm_hdmi_phy_powerdown()` call optional SoC-specific callbacks.
- `msm_hdmi_phy_pll_init()` selects the 8960, 8996, or 8998 PLL registration path.
- `msm_hdmi_phy_probe()` maps MMIO, initializes resources, initializes the PLL clock provider, and publishes drvdata.

## Control flow
Probe allocates `struct hdmi_phy`, pulls the matched `hdmi_phy_cfg`, maps `hdmi_phy`, initializes regulators/clocks by name, enables runtime PM, temporarily enables resources so PLL setup can touch hardware, registers the PLL provider where supported, disables resources again, and stores platform data. Driver registration exposes DT compatibles for 8660, 8960, 8974, 8084, 8996, and 8998.

## State and persistence
State lives in the devm-managed `struct hdmi_phy`: config pointer, MMIO base, regulator bulk array, clock array, and platform device. Resources are enabled only around PHY operations. The PLL registration persists as a clock provider for the device lifetime.

## Dependencies and integration points
Depends on OF match data, regulator bulk APIs, common clock framework helpers from SoC-specific PLL files, runtime PM, and `msm_ioremap()`/`msm_clk_get()`. It integrates with HDMI bridge power sequencing through `hdmi->phy`.

## Risks
`msm_hdmi_phy_resource_enable()` returns immediately on regulator failure without undoing runtime PM; clock enable failure does not unwind already enabled clocks. Probe must enable resources before PLL init because PLL register access depends on powered clocks/regulators. Unsupported PLL types intentionally succeed, which can mask missing PLL support.

## Test signals
Probe logs for missing regulators/clocks/MMIO, runtime PM balance, successful clock provider registration, HDMI mode set with each compatible, and suspend/resume of PHY resources are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/hdmi/hdmi_phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/hdmi/hdmi_phy_8960.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/hdmi/hdmi_phy_8960.c

## Purpose
Defines the simple MSM8960 HDMI PHY power sequencing and resource names.

## Important APIs, types, and functions
- `hdmi_phy_8960_powerup()` writes fixed PHY register values for analog setup and power-up.
- `hdmi_phy_8960_powerdown()` writes `0x7f` to power down the PHY.
- `msm_hdmi_phy_8960_cfg` advertises type, callbacks, one regulator, and one clock.

## Control flow
Power-up logs the pixel clock but does not vary programming by it. It writes REG2 low, fixed analog values to REG0/REG1, zeros several config registers, and writes REG3 `0x20`. Power-down writes the all-powerdown value to REG2.

## State and persistence
No software state is stored. Hardware register values persist while the PHY remains powered. Resource names are consumed by common `hdmi_phy.c`.

## Dependencies and integration points
Depends on `hdmi_phy_write()` and MSM8960 register definitions from `hdmi.h`. The config is referenced by the DT match table in `hdmi_phy.c`.

## Risks
The programming sequence is fixed and opaque, so changes require hardware validation. The ignored pixel clock means all modes rely on a single PHY tuning set while the PLL handles frequency.

## Test signals
Signals include successful modes on MSM8960 hardware, powerdown leakage/HPD behavior, and absence of PHY bring-up errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/hdmi/hdmi_phy_8960.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/hdmi/hdmi_phy_8996.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/hdmi/hdmi_phy_8996.c

## Purpose
Implements the MSM8996 HDMI QSERDES PHY PLL clock provider and PHY configuration data.

## Important APIs, types, and functions
- `struct hdmi_pll_8996` stores platform device, `clk_hw`, QSERDES common MMIO, and four TX lane MMIO bases.
- `struct hdmi_8996_phy_pll_reg_cfg` holds computed PLL, lane, drive, emphasis, mode, and comparator register values.
- `pll_get_post_div()` and `pll_calculate()` derive VCO, dividers, lock comparator, and lane programming from pixel clock and reference clock.
- `hdmi_8996_pll_set_clk_rate()`, `prepare()`, `unprepare()`, `determine_rate()`, `recalc_rate()`, and `is_enabled()` implement `clk_ops`.
- `msm_hdmi_pll_8996_init()` maps common/TX register windows and registers the `hdmipll` provider.

## Control flow
Rate setting computes bit clock as 10x pixel clock, chooses post dividers producing an 8-12 GHz VCO, calculates fractional PLL fields and thresholds, powers the PHY down/up, writes QSERDES common PLL registers, writes all TX lane drive and band settings, sets PHY mode, powers PHY blocks, and uses `wmb()` before PLL enable. `prepare()` toggles PHY config, polls QSERDES C_READY lock, enables TX transceivers, disables SSC, polls PHY ready, and restarts retiming. Rate requests are clamped to 25-600 MHz.

## State and persistence
The PLL object is devm-managed and registered as a clock provider. Hardware state lives in QSERDES common, TX lane, and HDMI PHY registers. Recalc reconstructs a rate from lock comparator registers instead of storing the requested value.

## Dependencies and integration points
Depends on common clock framework, OF clock provider registration, HDMI PHY drvdata from `hdmi_phy.c`, QSERDES register definitions, and `msm_ioremap()`. The HDMI modeset path drives it through the clock framework.

## Risks
PLL math and register values are mode-sensitive; incorrect divider selection can fail lock or produce wrong TMDS clocks. Poll helpers return boolean-like success rather than Linux error codes, so callers treat zero as failure. TX lane arrays assume exactly four channels. Recalc gives an approximate `fdata/10` result based on comparator state.

## Test signals
Check PLL lock/PHY ready debug logs, successful 25-600 MHz clock requests, high/mid/low TMDS modes, HDMI analyzer pixel clock, and mode changes across threshold boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/hdmi/hdmi_phy_8996.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/hdmi/hdmi_phy_8998.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/hdmi/hdmi_phy_8998.c

## Purpose
Implements the MSM8998 HDMI QSERDES PHY PLL provider and resource configuration, closely related to 8996 but with 8998-specific divider search and register programming.

## Important APIs, types, and functions
- `struct hdmi_pll_8998` stores platform device, `clk_hw`, last requested rate, QSERDES common MMIO, and four TX lane bases.
- `struct hdmi_8998_phy_pll_reg_cfg` contains calculated common PLL and TX lane fields.
- `pll_get_post_div()` selects VCO ratio, TX band, half-rate mode, and HSCLK divider with extra threshold checks.
- `pll_calculate()` derives PLL fractional fields, lock comparator, and drive settings for frequency ranges.
- `hdmi_8998_pll_*` functions implement clock rate, prepare, unprepare, recalc, and enable-state operations.

## Control flow
Rate setting calculates bit clock, selects a valid 8-12 GHz VCO that also satisfies comparator threshold ranges, fills common and TX lane config, powers down/up, writes QSERDES common PLL registers, writes TX interface/buffer/driver/emphasis/pre-driver/res-code registers, sets PHY mode, initializes lane config, flushes writes, and stores the requested rate. Prepare toggles PHY CFG values, polls lock, switches lane config to `0x1f`, polls PHY ready, restarts retiming, and flushes writes.

## State and persistence
The software PLL object stores `rate` because recalc returns the last requested clock instead of decoding hardware. Hardware state persists in 8998 QSERDES and PHY registers while powered. The config advertises regulators `vddio`, `vcca` and clocks `iface`, `ref`, `xo`.

## Dependencies and integration points
Depends on common clock framework, OF clock provider registration, `hdmi_phy.c` drvdata, and 8998 register macros. HDMI modeset uses the registered `hdmipll`.

## Risks
The divider search has more constraints than 8996; unsupported frequencies return `-EINVAL`. Stored-rate recalc can be stale after hardware reset. Poll failures return zero, which is not a conventional negative errno. Frequency threshold-specific drive settings need hardware validation across modes.

## Test signals
Validate PLL lock and PHY ready across low, mid, digital, and high frequency thresholds, HDMI pixel clock accuracy, mode switches after suspend/resume, and clock provider probe with all three clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/hdmi/hdmi_phy_8998.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/hdmi/hdmi_phy_8x60.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/hdmi/hdmi_phy_8x60.c

## Purpose
Programs power-up and power-down sequences for the older 8x60 HDMI PHY.

## Important APIs, types, and functions
- `hdmi_phy_8x60_powerup()` sequences deserializer delay, swing level, power generator, PLL, drivers, lock detect, retiming, and receive sense.
- `hdmi_phy_8x60_powerdown()` resets the PHY, powers down drivers/PLL/power generator, and leaves receive sense enabled.
- `msm_hdmi_phy_8x60_cfg` exposes callbacks plus `core-vdda` regulator and `slave_iface` clock.

## Control flow
Power-up selects output swing based on 27 MHz pixel clock versus other modes, starts from full powerdown, incrementally enables power generator, PLL, ASIC power, lock detect, retiming, drivers, and receive sense, clears several registers, then forces lock detection. Power-down asserts/deasserts controller reset, disables drivers, disables PLL, and powers down most blocks.

## State and persistence
There is no software state. Register programming persists while the PHY is powered and is reset by powerdown or platform reset.

## Dependencies and integration points
Depends on `hdmi_phy_write()`, register bit macros, and the common HDMI PHY platform driver.

## Risks
Timing delays are short and hardware-specific. The special 27 MHz swing setting can affect only SD modes. Leaving receive sense enabled is intentional for cable detection and should not be removed without HPD validation.

## Test signals
Validate 27 MHz and non-27 MHz modes, hotplug after powerdown, PHY lock/stability, and current draw in powerdown with RX sense.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/hdmi/hdmi_phy_8x60.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/hdmi/hdmi_phy_8x74.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/hdmi/hdmi_phy_8x74.c

## Purpose
Defines minimal 8x74/8084 HDMI PHY register programming and resource names.

## Important APIs, types, and functions
- `hdmi_phy_8x74_powerup()` writes fixed analog, BIST, pattern, and power-control register values.
- `hdmi_phy_8x74_powerdown()` writes `0x7f` to power-control register 0.
- `msm_hdmi_phy_8x74_cfg` supplies callbacks, two regulators, and two clocks.

## Control flow
Power-up writes ANA_CFG0/1, clears BIST and pattern registers, and writes PD_CTRL1 `0x20`. Power-down writes PD_CTRL0 `0x7f`. Pixel clock is accepted by the callback but not used.

## State and persistence
No software state. PHY register state persists while resources remain enabled.

## Dependencies and integration points
Depends on `hdmi_phy_write()` and the DT match table in `hdmi_phy.c`, where both 8974 and 8084 compatibles map to this config.

## Risks
The fixed configuration may not cover all board-level signal integrity needs. Powerdown and powerup touch different power-control registers, so sequencing assumptions are hardware-specific.

## Test signals
Successful HDMI modes on 8974/8084, PHY powerdown recovery, and signal integrity across standard pixel clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/hdmi/hdmi_phy_8x74.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/hdmi/hdmi_pll_8960.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/hdmi/hdmi_pll_8960.c

## Purpose
Registers and programs the MSM8960 HDMI PLL as a common-clock provider using a fixed table of supported pixel-clock configurations.

## Important APIs, types, and functions
- `struct hdmi_pll_8960` stores platform device, `clk_hw`, MMIO base, and current pixel clock.
- `struct pll_rate` and `freqtbl[]` map target pixel clocks to ordered register writes.
- `find_rate()` chooses the closest table entry at or above the requested rate according to descending table order.
- `hdmi_pll_enable()`, `disable()`, `determine_rate()`, `set_rate()`, and `recalc_rate()` implement `clk_ops`.
- `msm_hdmi_pll_8960_init()` maps the PLL, sanity-checks table order, registers `hdmi_pll`, and adds the OF clock provider.

## Control flow
`set_rate()` finds a table row and writes all configured PLL registers, then stores the requested rate in `pixclk`. `determine_rate()` snaps requests to a table-supported rate. Enable asserts/deasserts PLL software reset, toggles PHY reset/power bits, powers the PLL, then polls the lock bit with retries and software-reset attempts. Disable clears PHY global power and PLL power bits.

## State and persistence
Software state is the stored `pixclk`. Hardware state is the PLL register table and power/lock bits. The clock provider remains registered for the device lifetime.

## Dependencies and integration points
Depends on common clock framework, OF provider helpers, MSM8960 HDMI PHY register access via `pll_get_phy()`, and `msm_ioremap()`. Used by HDMI modeset through clock APIs.

## Risks
Only table-supported rates are accurate; `pixclk` stores the requested rate rather than the snapped table rate. `hdmi_pll_enable()` returns success even if lock polling never observes lock. Table order validation only checks descending rates at init.

## Test signals
Validate `determine_rate()` snapping, PLL lock bit behavior, 25.2/27/74.176/74.25/148.5 MHz modes, clock provider registration, and behavior after failed lock retries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/hdmi/hdmi_pll_8960.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_atomic.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_atomic.c

## Purpose
Implements MSM DRM atomic check and commit tail sequencing, including asynchronous single-CRTC cursor/async updates scheduled just before vblank.

## Important APIs, types, and functions
- `msm_atomic_check()` runs MSM KMS mode-change checks and DRM atomic helper validation, with CTM changes forced through modeset.
- `msm_atomic_commit_tail()` is the main hardware commit sequence.
- `msm_atomic_init_pending_timer()` and `msm_atomic_destroy_pending_timer()` create per-CRTC FIFO kthread workers and hrtimer work.
- Helpers manage vblank refs, per-CRTC commit locks, pending mask, and async eligibility.
- Tracepoints from `msm_atomic_trace.h` instrument commit and flush phases.

## Control flow
Commit tail enables commit access, locks affected CRTC commit locks, waits for any previous flush, clears fault snapshot capture, optionally prepares the commit, pushes modeset disables, planes, and enables through DRM helpers, then either schedules async flush work or executes a synchronous flush. Async mode is allowed only for legacy cursor or async updates with no connector changes, no modeset, active state, and exactly one CRTC. The async path queues timer work one millisecond before the next vblank, immediately signals DRM commit completion, and lets the worker flush/wait/complete later under the same CRTC lock.

## State and persistence
Uses `kms->pending_crtc_mask`, `kms->commit_lock[]`, `kms->pending_timers[]`, `kms->fault_snapshot_capture`, and runtime vblank references. It does not persist state beyond current KMS runtime.

## Dependencies and integration points
Depends on `struct msm_kms` function callbacks (`enable_commit`, `prepare_commit`, `flush_commit`, `wait_flush`, `complete_commit`, `disable_commit`, `check_mode_changed`), DRM atomic helpers, DRM vblank helpers, hrtimer work, and tracepoints.

## Risks
Async completion reports hardware done to DRM before the actual flush, so ordering relies on pending masks and locks. Failure to get next vblank falls back to synchronous flush. Commit locks must be acquired/released in deterministic CRTC order to avoid deadlocks. CTM changes force modeset as a FIXME.

## Test signals
Use tracepoints for commit start/finish, flush, and wait phases. Exercise cursor async updates, multi-CRTC commits, CTM changes, vblank event timestamps, fallback when next vblank is unavailable, and suspend/destroy of pending timers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_atomic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_atomic_trace.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_atomic_trace.h

## Purpose
Defines ftrace trace events for MSM atomic commit phases.

## Important APIs, types, and functions
- `TRACE_EVENT(msm_atomic_commit_tail_start/finish)` records async flag and CRTC mask.
- `TRACE_EVENT(msm_atomic_async_commit_start/finish)` records the async worker CRTC mask.
- `TRACE_EVENT(msm_atomic_wait_flush_start/finish)` and `TRACE_EVENT(msm_atomic_flush_commit)` mark flush wait and issue points.
- `TRACE_SYSTEM` is `drm_msm_atomic`, with include path adjusted for generated trace code.

## Control flow
The header has declarative tracepoint definitions only. Runtime control flow is in `msm_atomic.c`, which calls the generated `trace_msm_atomic_*()` functions around commit operations.

## State and persistence
No persistent driver state. Trace records are emitted to the kernel tracing buffers when enabled.

## Dependencies and integration points
Depends on Linux tracepoint infrastructure and `msm_atomic_tracepoints.c` defining `CREATE_TRACE_POINTS`. Integrated directly by `msm_atomic.c`.

## Risks
Trace ABI names are useful for debugging and tests; renaming them can break scripts. The include guard allows multi-read for trace generation and must preserve tracepoint conventions.

## Test signals
Build coverage of trace generation and runtime visibility under `/sys/kernel/tracing/events/drm_msm_atomic/` are primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_atomic_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_atomic_tracepoints.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_atomic_tracepoints.c

## Purpose
Instantiates the MSM atomic tracepoints declared in `msm_atomic_trace.h`.

## Important APIs, types, and functions
- Defines `CREATE_TRACE_POINTS`.
- Includes `msm_atomic_trace.h`.

## Control flow
There is no runtime logic beyond tracepoint object generation at build time.

## State and persistence
No driver state is stored here. Generated tracepoint definitions become static kernel instrumentation points.

## Dependencies and integration points
Depends entirely on Linux tracepoint build conventions and must be compiled exactly once for the trace header.

## Risks
If this file is omitted or duplicated, tracepoint linkage can fail. It must stay tiny and synchronized with the header.

## Test signals
Build/link success and available `drm_msm_atomic` trace events confirm correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_atomic_tracepoints.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_debugfs.c

## Purpose
Creates MSM DRM debugfs files for GPU snapshots, KMS snapshots, framebuffer/GEM/MM state, shrinker control, fault injection, and GPU devfreq/hangcheck knobs.

## Important APIs, types, and functions
- `msm_debugfs_init()` registers common, GPU, KMS, shrinker, and fault-injection files.
- `msm_debugfs_late_init()` registers rd/perf debugfs on primary/render minors after DRM registration.
- GPU snapshot path: `msm_gpu_open()`, `msm_gpu_show()`, `msm_gpu_release()`.
- KMS snapshot path: `msm_kms_open()`, `msm_kms_show()`, `msm_kms_release()`.
- Debug entries include `gem`, `mm`, `fb`, `gpu`, `kms`, `shrink`, `stall_reenable_time_us`, and devfreq knobs.

## Control flow
Opening `gpu` locks the GPU, runtime-resumes it, initializes hardware, captures GPU state through GPU callbacks, and later prints/releases that snapshot. Opening `kms` locks `kms->dump_mutex`, captures a display snapshot, and prints it. `gem` walks the global object list under `obj_lock`; `fb` walks fbdev and framebuffer lists; `shrink` invokes the GEM shrinker and stores the last freed count. Late init installs rd/perf files only when a GPU platform device exists.

## State and persistence
Persistent debug state includes `last_shrink_freed` and writable driver fields such as hangcheck period, error IRQ disable, devfreq thresholds, and idle clamp. Snapshot objects are allocated per open and freed at release.

## Dependencies and integration points
Depends on CONFIG_DEBUG_FS, DRM debugfs helpers, fb helper, GPU/KMS callback interfaces, display snapshot code, GEM shrinker, fault injection attributes, and rd/perf debugfs modules.

## Risks
Debugfs reads can resume and initialize GPU hardware, so they are not passive. Snapshot capture and release must hold GPU/KMS locks correctly. Writable debug knobs are test-oriented and can alter hang detection or devfreq behavior. `last_shrink_freed` is global rather than per-device.

## Test signals
Check debugfs file creation on primary/render nodes, GPU and KMS snapshot reads, `gem`/`mm`/`fb` output, shrink write/read behavior, fault injection files, and lockdep under concurrent debugfs access/removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_debugfs.h

## Purpose
Declares the debugfs initialization hook for MSM DRM when debugfs is enabled.

## Important APIs, types, and functions
- Include guard `__MSM_DEBUGFS_H__`.
- Conditional declaration `void msm_debugfs_init(struct drm_minor *minor);` under `CONFIG_DEBUG_FS`.

## Control flow
No runtime control flow. It exposes `msm_debugfs_init()` to the DRM driver definition while compiling away the declaration when debugfs is disabled.

## State and persistence
No state is defined.

## Dependencies and integration points
Included by `msm_drv.c` and implemented by `msm_debugfs.c`. The actual fallback for no debugfs is handled by conditional driver fields and other stubs.

## Risks
Signature drift breaks driver initialization builds. The header intentionally stays narrow.

## Test signals
Build MSM DRM with and without `CONFIG_DEBUG_FS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_drv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_drv.c

## Purpose
Implements the top-level MSM DRM driver: module parameters, DRM device allocation/registration, component binding, per-file contexts, IOCTL dispatch, GPU/KMS split-device support, and module init/exit registration of subdrivers.

## Important APIs, types, and functions
- Module params: `dumpstate`, `modeset`, `separate_gpu_kms`, and optional `prefer_mdp5`.
- `msm_drm_init()`/`msm_drm_uninit()` allocate, bind, register, debugfs-init, and tear down DRM devices.
- `msm_open()`, `msm_postclose()`, `context_init()`, and `context_close()` manage per-file `msm_context`.
- IOCTL handlers cover params, GEM create/info/cpu prep/fini/madvise, submit queues, wait fence, submit, and VM_BIND.
- `msm_drv_probe()`, `msm_gpu_probe()`, `msm_gpu_remove()`, and component ops integrate display/GPU platform devices.

## Control flow
Module init registers display, HDMI, DP, DSI, GPU, MDP, DPU, and MDSS subdrivers unless modeset is disabled. Probe builds a component match list from MDP graph endpoints and optional GPU nodes, sets DMA masks, and registers a component master. `msm_drm_init()` allocates `drm_device`, initializes object/LRU/fault-stall state, initializes KMS mode config when needed, binds components, starts the GEM shrinker, initializes KMS, registers DRM, and then initializes late debugfs/post-init. Open lazily loads the GPU and creates a context. Close disables sysprof and closes submit queues.

## State and persistence
Driver-private state lives in `struct msm_drm_private`, including KMS/GPU pointers, GEM object list, LRUs, shrinker, debug state, devfreq config, and fault-stall state. Per-file state is `struct msm_context`, submit queues, VM, sequence number, and memory accounting. IOCTL metadata/name state is stored on GEM objects.

## Dependencies and integration points
Depends on DRM core, component framework, OF graph helpers, Adreno GPU loader, KMS implementations, GEM/shrinker, debugfs/perf/rd modules, submitqueue and VM_BIND code, dma-fence, syncobj, and PRIME import/export hooks.

## Risks
Initialization/unwind ordering is complex: DRM unregister, KMS unregister/uninit, shrinker cleanup, debugfs cleanup, GPU/component unbind, and drm_dev_put must stay ordered. Lazy GPU load on open means render users may see ENXIO before firmware/GPU availability. GEM_INFO metadata size and string handling are UABI-visible. `separate_gpu_kms` changes component topology and driver feature sets.

## Test signals
Probe/remove for combined and split GPU/KMS devices, all IOCTL validation paths, GEM fault injection, metadata get/set, submitqueue lifecycle, wait fence timeout/boost, component graph variations, and module unload are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_drv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_drv.h

## Purpose
Central MSM DRM private header declaring shared driver state, feature glue, subsystem entry points, helpers, and configuration stubs.

## Important APIs, types, and functions
- `struct msm_drm_private` holds DRM device, KMS/GPU pointers, GEM object/LRU/shrinker state, debug handles, hangcheck/devfreq config, and fault-stall fields.
- Controller enums define DP and DSI controller IDs and `MSM_GPU_MAX_RINGS`.
- Declares atomic, MMU, GEM, PRIME, framebuffer, fbdev, HDMI, DSI, DP, MDP, DPU, MDSS, debugfs, IO remap, ICC, hrtimer work, probe, and shutdown APIs.
- Helpers include `msm_rmw()`, `align_pitch()`, `timeout_to_jiffies()`, `UERR`, `DBG`, `FIELD`, and `COND`.
- Conditional stubs compile out disabled subsystems.

## Control flow
Mostly declarative. Inline helpers perform read-modify-write, pitch alignment to 32 pixels, absolute timeout conversion to jiffies, and disabled-subsystem no-op/error behavior.

## State and persistence
The main persistent state definition is `struct msm_drm_private`, owned by `msm_drv.c` and shared by GPU/KMS/GEM/debugfs code. No storage is allocated by the header.

## Dependencies and integration points
Pulls together Linux platform/component/PM/IOMMU/devfreq headers, DRM atomic/probe/DSC/GEM/UAPI headers, and internal subsystem declarations. Almost every MSM DRM file depends on it.

## Risks
Because this is a broad private ABI, structure changes can affect many modules. Conditional stubs must match real signatures. `timeout_to_jiffies()` treats expired deadlines as zero, influencing wait IOCTL behavior. Global helper macros like `FIELD()` depend on generated mask/shift names.

## Test signals
Build coverage across configurations with HDMI/DSI/DP/MDP/DPU/MDSS/debugfs/fbdev enabled and disabled, plus runtime checks of timeout and pitch helper behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_dsc_helper.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_dsc_helper.h

## Purpose
Provides a shared MSM helper for Display Stream Compression line-size calculations used by DSI, DP, and timing-engine code.

## Important APIs, types, and functions
- `msm_dsc_get_bytes_per_line(const struct drm_dsc_config *dsc)` returns `slice_count * slice_chunk_size`.

## Control flow
Single inline arithmetic helper; no branching.

## State and persistence
No state.

## Dependencies and integration points
Depends on `drm/display/drm_dsc_helper.h` and `struct drm_dsc_config`. Callers convert this byte count into interface-specific timing values such as pclk-per-interface.

## Risks
The helper assumes `slice_chunk_size` is already computed correctly by DRM DSC helpers. Widebus or interface division must be handled by callers, not here.

## Test signals
Compile coverage and caller tests comparing DSI/DP timing math against expected DSC slice counts and chunk sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_dsc_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_fb.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_fb.c

## Purpose
Implements MSM framebuffer objects, scanout preparation/cleanup, dirtyfb propagation, framebuffer creation/validation, debug descriptions, and stolen/regular fb allocation.

## Important APIs, types, and functions
- `struct msm_framebuffer` extends `drm_framebuffer` with MSM format, dirtyfb refcount, per-plane IOVA, and prepare count.
- `msm_framebuffer_create()` looks up GEM handles and calls the internal initializer.
- `msm_framebuffer_prepare()` pins all plane BOs into the KMS VM and records IOVAs.
- `msm_framebuffer_cleanup()` unpins plane BOs and clears IOVAs when prepare count reaches zero.
- `msm_alloc_stolen_fb()` allocates fbdev-style scanout buffers, preferring stolen memory.

## Control flow
Create validates plane objects, format support via `mdp_get_format()`, plane sizes including offsets/pitches/subsampling, and rejects `MSM_BO_NO_SHARE` because scanout maps into the KMS VM. Prepare increments dirtyfb when needed, uses `prepare_count` to avoid duplicate pinning, gets VMA refs, and pins IOVAs for each plane. Cleanup mirrors this by decrementing dirtyfb, unpinning IOVAs, and dropping VMA refs on the final cleanup.

## State and persistence
Framebuffer state persists in `struct msm_framebuffer` while the DRM framebuffer exists. Per-plane IOVAs are valid only while prepared. Dirtyfb refcount tracks whether users of the fb need pixel flush handling.

## Dependencies and integration points
Depends on DRM framebuffer/GEM helpers, MSM KMS VM, GEM IOVA helpers, MDP format lookup, dirtyfb helper, and fbdev allocation path.

## Risks
If pinning one plane fails after earlier planes are pinned, the function returns without local unwind, relying on callers/error paths to cleanup. `prepare_count` and dirtyfb refcount must stay balanced. Plane size validation must match DRM format subsampling to prevent scanout beyond BO size.

## Test signals
Framebuffer creation with multi-plane formats, invalid pitches/offsets/sizes, NO_SHARE rejection, repeated prepare/cleanup balance, dirtyfb behavior, and stolen-memory fallback are useful tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_fb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_fbdev.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_fbdev.c

## Purpose
Implements the optional legacy fbdev compatibility layer for MSM DRM.

## Important APIs, types, and functions
- Module parameter `fbdev` enables/disables fbdev compatibility.
- `msm_fbdev_driver_fbdev_probe()` allocates framebuffer backing BO, pins it for scanout, maps it to CPU, and fills `fb_info`.
- `msm_fbdev_mmap()` maps the backing GEM object through PRIME mmap.
- `msm_fbdev_fb_destroy()` tears down helper, CPU vmap, framebuffer, and DRM client.
- `msm_fbdev_fb_dirty()` forwards fbdev damage to framebuffer dirty handling.

## Control flow
Probe selects a legacy DRM format, aligns pitch with `align_pitch()`, allocates a stolen or regular scanout framebuffer, pins its BO into KMS VM for physical/start address reporting, assigns helper funcs and fb ops, fills fb info, gets a CPU vaddr, and sets `screen_buffer`, `screen_size`, `smem_start`, and `smem_len`. Dirty ignores empty clips and forwards real damage through fb dirty callbacks.

## State and persistence
State is held by the DRM fb helper, fb_info, framebuffer, pinned BO IOVA, and CPU vmap while fbdev is active. Destroy releases those resources.

## Dependencies and integration points
Depends on DRM fb helper, GEM PRIME mmap, MSM framebuffer and GEM helpers, KMS VM, and deferred sysmem fb ops.

## Risks
The failure path after pinning/vmap setup removes the framebuffer but does not explicitly unpin the IOVA in this file; correctness depends on framebuffer/GEM teardown. The global `fbdev` parameter is declared here but higher-level DRM fbdev behavior must respect driver ops. Panic-console assumptions rely on the BO being pinned and CPU-mapped.

## Test signals
Boot fbcon, mmap from fbdev, deferred damage propagation, probe failure unwinds, suspend/resume, and module parameter behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_fbdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_fence.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_fence.c

## Purpose
Implements MSM GPU fence contexts and dma-fence objects, including deadline-driven GPU devfreq boosting.

## Important APIs, types, and functions
- `msm_fence_context_alloc()` and `msm_fence_context_free()` create/free per-ring fence timelines.
- `msm_fence_completed()` checks completed seqnos using both CPU cached value and GPU-written fence pointer.
- `msm_update_fence()` updates completed fence state and cancels deadline timers.
- `msm_fence_alloc()` allocates a fence object; `msm_fence_init()` initializes it with dma-fence ops.
- `msm_fence_set_deadline()` schedules boost work just before a fence deadline.

## Control flow
Contexts start near `0xffffff00` to exercise rollover comparisons. Fence completion uses signed 32-bit subtraction for wrap-safe ordering. Deadline setting records the earliest next deadline, tracks the associated fence, and either queues boost immediately or starts an hrtimer for 3 ms before the deadline. Timer expiry queues work on the GPU worker, and the worker boosts devfreq if the deadline fence has not completed.

## State and persistence
`struct msm_fence_context` stores context ID, local index, last/completed fence seqnos, GPU fence pointer, spinlock, hrtimer, deadline work, next deadline, and deadline fence. Each `struct msm_fence` stores its dma-fence and context pointer.

## Dependencies and integration points
Depends on dma-fence, hrtimer, kthread work, MSM GPU worker/devfreq, and `struct msm_drm_private->gpu`. Used by GPU submit/ring code and wait-fence IOCTLs.

## Risks
Deadline boost assumes a valid GPU worker. `msm_fence_context_free()` does not cancel hrtimer/work itself, so users must destroy contexts after work is quiesced. Wraparound comparisons are intentional and must not be replaced with plain integer comparisons.

## Test signals
Fence rollover tests, wait-fence behavior, deadline boost triggering/canceling, GPU-written fence pointer fast completion, and context teardown under no pending timer/work are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_fence.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_fence.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_fence.h

## Purpose
Declares MSM fence context state, fence lifecycle APIs, and wrap-safe fence comparison helpers.

## Important APIs, types, and functions
- `struct msm_fence_context` documents per-ring timeline state, GPU fence pointer, spinlock, deadline timer, and deadline work.
- Declares `msm_fence_context_alloc/free()`, `msm_fence_completed()`, `msm_update_fence()`, `msm_fence_alloc()`, and `msm_fence_init()`.
- Inline `fence_before()` and `fence_after()` use signed 32-bit subtraction for seqno wraparound.

## Control flow
The header has no complex runtime flow; only inline comparisons execute.

## State and persistence
Defines the persistent fence context layout used by `msm_fence.c` and GPU ring code.

## Dependencies and integration points
Includes `msm_drv.h` for DRM/device types and is consumed by submit, ring, and wait paths.

## Risks
Changing struct fields or comparison semantics affects synchronization correctness across the driver. Deadline fields currently track only one next deadline and are documented as limited for multiple queued deadlines.

## Test signals
Build coverage plus rollover comparison unit-style checks and submit/wait tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_fence.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_gem.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_gem.c

## Purpose
Implements MSM GEM buffer object lifetime, page backing, CPU mmap/vmap, IOVA/VMA management, LRU and shrinker-facing state, madvise/purge/evict behavior, dumb buffers, imported buffers, kernel BO helpers, and debug descriptions.

## Important APIs, types, and functions
- Object lifecycle: `msm_gem_new()`, `msm_gem_new_handle()`, `msm_gem_import()`, `msm_gem_free_object()`.
- Backing/page APIs: `msm_gem_get_pages_locked()`, `msm_gem_pin_pages_locked()`, `msm_gem_unpin_pages_locked()`, `put_pages()`.
- VM/IOVA APIs: `msm_gem_get_iova()`, `msm_gem_set_iova()`, `msm_gem_get_and_pin_iova*()`, `msm_gem_unpin_iova()`, `msm_gem_pin_vma_locked()`.
- CPU APIs: `msm_gem_get_vaddr*()`, `msm_gem_put_vaddr*()`, `msm_gem_cpu_prep()`, `msm_gem_cpu_fini()`, mmap fault ops.
- Memory pressure/debug APIs: `msm_gem_madvise()`, `msm_gem_purge()`, `msm_gem_evict()`, `msm_gem_vunmap()`, `msm_gem_describe*()`.

## Control flow
Objects start unbacked in the unbacked LRU. Page allocation locks the object, gets shmem pages, updates memory accounting tracepoints, creates an SG table, performs cache sync for WC buffers, and moves the object to an active LRU. IOVA lookup creates or reuses a GPUVA under VM and object locks via `drm_exec`; pinning maps the VMA with IOMMU prot flags and increments pin counts. Unpinning updates LRU state and closes non-KMS VMAs when appropriate. Close paths drop context memory accounting and tear down legacy kernel-managed VM mappings, while VM_BIND contexts defer teardown to VM close.

CPU fault/vmap paths allocate backing pages on demand, reject purged buffers, insert PFNs for mmap, and pin while vmap references exist. Madvise moves objects between WILLNEED/DONTNEED/PURGED states. Purge unmaps IOVAs, vunmaps, unmaps CPU VMAs, drops backing pages, marks purged, frees mmap offset, and truncates shmem. Evict drops mappings/pages without marking purged. Free removes the object from global lists, tears down GPUVA mappings with VM locks, handles imported sg tables differently from owned pages, drops shared-resv references for NO_SHARE, releases GEM core state, metadata, and object memory.

## State and persistence
State is in `struct msm_gem_object`: flags, madv, vmap count, global list node, pages, sg table, vaddr, debug name, metadata, pin count, and VMA refcount. Device-wide state includes total memory accounting, global object list, and LRUs. Per-file memory accounting is updated on open/close.

## Dependencies and integration points
Depends on DRM GEM/shmem/PRIME/GPUVM/drm_exec, dma-resv, dma mapping, vmalloc, DRM format helpers, trace `gpu_mem`, MSM MMU/VMA helpers, shrinker code, KMS VM, and PRIME export/import callbacks.

## Risks
Lock ordering is subtle: object locks, VM reservation objects, LRU lock, obj list lock, and fs reclaim require the documented special cases. Pin counts and VMA references must stay balanced or memory cannot be purged. Imported buffers are permanently treated as pinned/resident. Purge/evict must avoid active or pinned objects. `MSM_BO_NO_SHARE` swaps reservation objects and changes sharing semantics.

## Test signals
Exercise GEM create/open/close/free, mmap faults after madvise/purge, IOVA get/set/pin/unpin, VM_BIND versus legacy VM teardown, shrinker purge/evict, PRIME import/export, NO_SHARE rejection, CPU prep timeout/boost, memory accounting tracepoints, and lockdep under concurrent submit/shrinker/close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_gem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_gem.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_gem.h

## Purpose
Defines MSM GEM, GPU VM, VMA, and submit data structures plus helper APIs used by GEM memory management, VM_BIND, KMS scanout, PRIME, and submit paths.

## Important APIs, types, and functions
- Internal BO flags `MSM_BO_STOLEN` and `MSM_BO_MAP_PRIV`.
- `struct msm_gem_vm` wraps `drm_gpuvm` with scheduler, preallocation throttle, kernel-managed `drm_mm`, MMU, PID, last fence, VM update log, fault count, managed/unusable flags.
- `struct msm_gem_vma` wraps `drm_gpuva` with optional `drm_mm_node` and mapped flag.
- `struct msm_gem_object` extends `drm_gem_object` with flags, madv, vmap count, backing pages/sgt/vaddr, name, metadata, pin count, and VMA refcount.
- `struct msm_gem_submit` tracks scheduler job, refs, VM, exec lock context, fences, submit queue, command buffers, BOs, ring, and flags.
- Inline locks and helpers wrap dma-resv, `drm_exec`, and purgeability checks.

## Control flow
Most content is declarative. `msm_gem_lock_vm_and_obj()` uses `drm_exec` to lock a VM reservation object and a BO reservation object with contention retry. `msm_gem_assert_locked()` allows the free path to look locked when refcount is zero to avoid lockdep false positives. Purgeability helpers classify objects based on import status, pin count, vmap count, and madv.

## State and persistence
This header defines the state carried by GEM objects, VMs, VMAs, and submits throughout object, VM, and job lifetimes. The VM log persists recent VM updates for devcore dumps.

## Dependencies and integration points
Depends on DRM GPUVM, DRM scheduler, DRM exec, dma-resv, MSM MMU, and `msm_drv.h`. Used by GEM, submit, VM_BIND, GPU, KMS, debugfs, and PRIME files.

## Risks
Struct layout and locking helpers are central to driver correctness. VM_BIND permits multiple VMAs per BO per VM, unlike older lookup paths that assume one VMA; callers must use the right API. `vma_ref` intentionally holds lazy KMS VMAs and must be balanced by exports/handles.

## Test signals
Compile coverage plus VM_BIND mapping/unmapping, legacy GEM_INFO IOVA behavior, submit teardown, shrinker classification, and lockdep validation of `msm_gem_lock_vm_and_obj()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_gem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_gem_prime.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_gem_prime.c

## Purpose
Implements MSM GEM PRIME/dma-buf import, export, pin, unpin, and vmap support.

## Important APIs, types, and functions
- `msm_gem_prime_get_sg_table()` exports pinned backing pages as an SG table.
- `msm_gem_prime_vmap()` and `msm_gem_prime_vunmap()` map/unmap GEM objects to kernel virtual addresses.
- `msm_gem_prime_import()` handles same-device self-import specially, otherwise delegates to DRM PRIME import.
- `msm_gem_prime_import_sg_table()` creates an MSM imported GEM object from an attachment SG table.
- `msm_gem_prime_export()` builds a dma-buf with MSM-specific release handling.
- `msm_gem_prime_pin()` and `msm_gem_prime_unpin()` pin owned backing pages for dma-buf access.

## Control flow
Export rejects `MSM_BO_NO_SHARE`, increments the GEM VMA refcount to keep lazy mappings alive, and exports a dma-buf with custom ops whose release drops that VMA ref before the DRM dma-buf release. Import detects dma-bufs exported by the same ops on the same device and returns a GEM object reference directly; external imports use DRM helpers and `msm_gem_import()`. Pin skips already imported objects, rejects NO_SHARE, and pins backing pages under the caller-held object lock.

## State and persistence
Exported dma-bufs hold a GEM reference through DRM core and an extra VMA ref until release. Imported objects store external SG table/page arrays in `msm_gem_object` and are treated as imported by GEM core.

## Dependencies and integration points
Depends on DRM PRIME/dma-buf helpers, GEM page/vmap helpers, and `msm_gem_import()`. Integrated through `drm_gem_object_funcs` and `drm_driver` PRIME hooks.

## Risks
`get_sg_table()` assumes pages were already pinned; otherwise it returns an error. NO_SHARE objects must never be exported/imported through PRIME. Vmap helpers assume the object lock context expected by GEM PRIME callbacks.

## Test signals
Same-device self-import, external dma-buf import/export, NO_SHARE rejection, pin/unpin balance, vmap/vunmap, and release dropping VMA refs are key tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_gem_prime.c -->
