# subset-b-001076 grouped code research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/n2-drv.c -->
# sources/distributed-fs/ceph-client/drivers/char/hw_random/n2-drv.c

Purpose: SPARC sun4v Niagara2/VF/KT/M4/M7 hardware RNG driver that exposes the hypervisor RNG through the Linux `hwrng` core. It supports guest read-only use and control-domain configuration/self-test.

Important APIs, types, and functions: `struct n2rng`, `struct n2rng_unit`, `n2rng_probe()`, `n2rng_remove()`, `n2rng_data_read()`, `n2rng_work()`, `n2rng_control_selftest()`, `n2rng_control_configure_units()`, and hypervisor wrappers around `sun4v_rng_*`. Device matching selects `struct n2rng_template` for chip version and multi-unit capability.

Control flow: probe registers RNG HVAPI v2 then v1 fallback, allocates per-unit control state, detects control-domain access, registers `hwrng`, and schedules delayed work. Work either performs guest data-read validation or, in control domain, disables preemption, runs diagnostic self-tests per unit, configures control registers, and marks `N2RNG_FLAG_READY`. Reads return cached upper/lower halves of a 64-bit HV read and schedule retest on failures.

State and persistence: state is in flags, per-unit control arrays, HV API version, health parameters, and delayed work. No disk persistence. `N2RNG_FLAG_SHUTDOWN` prevents retry work after remove.

Dependencies and integration: depends on SPARC hypervisor APIs, OF platform matching, `hwrng`, delayed work, physical-address-safe buffers, and `n2rng.h` constants/assembly entry points.

Risks and test signals: risks include HV busy/block retry limits, static `retries` shared across devices in `n2rng_work()`, control-domain self-test timing, multi-unit `rng-#units` DT property correctness, and physical address alignment. Tests should exercise HVAPI v1/v2 fallback, guest vs control behavior, self-test failure retry, remove during delayed work, and hwrng read recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/n2-drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/n2rng.h -->
# sources/distributed-fs/ceph-client/drivers/char/hw_random/n2rng.h

Purpose: shared Niagara2 RNG definitions for the C driver and related assembly hypervisor call stubs.

Important APIs, types, and functions: defines v1/v2 control bitfields, hypervisor function numbers, HV RNG states, `enum n2rng_compat_id`, `struct n2rng_template`, `struct n2rng_unit`, and `struct n2rng`. It declares `sun4v_rng_get_diag_ctl()`, control read/write helpers, diagnostic data reads, and normal data reads.

Control flow: this header has no executable flow, but it defines the contract used by `n2-drv.c`: control register layout differs by chip generation, HV API v1 lacks per-unit arguments while v2 includes units/watchdog status, and shared state values move hardware between unconfigured, configured, healthcheck, and error states.

State and persistence: all persistent runtime state is represented in `struct n2rng`: flags, unit count/control words, hwrng object, cached `u32` buffer, HV API version, delayed work, health parameters, scratch/test buffers, and test controls.

Dependencies and integration: included by `n2-drv.c` and assembly code; requires Linux types and hwrng/platform declarations on the C side and avoids C declarations under `__ASSEMBLER__`.

Risks and test signals: bitfield drift would silently misprogram entropy sources. Tests should verify compile coverage for assembly/C users, chip-version-specific control masks, struct field assumptions used by the driver, and limits such as `N2RNG_BLOCK_LIMIT`, `N2RNG_BUSY_LIMIT`, and self-test constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/n2rng.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/nomadik-rng.c -->
# sources/distributed-fs/ceph-client/drivers/char/hw_random/nomadik-rng.c

Purpose: AMBA driver for the ST-Ericsson Nomadik RNG block, exposing a single 16-bit sample through `hwrng`.

Important APIs, types, and functions: global `struct hwrng nmk_rng`, `nmk_rng_read()`, `nmk_rng_probe()`, `nmk_rng_remove()`, and AMBA ID table `nmk_rng_ids`.

Control flow: probe enables the clock, requests AMBA regions, ioremaps the resource, stores the base address in `nmk_rng.priv`, and registers with `devm_hwrng_register()`. Reads fetch one 32-bit register at offset 8, mask to the lower 16 bits, and return 2 bytes regardless of `wait`.

State and persistence: state is the global hwrng object's `priv` base pointer; the driver assumes at most one device. No persistence beyond device lifetime.

Dependencies and integration: depends on AMBA bus probing, `devm_clk_get_enabled()`, AMBA resource ownership, raw MMIO access, and hwrng core.

Risks and test signals: the global `nmk_rng` is not multi-instance safe; read writes a `u16` to caller buffer and assumes alignment. Tests should cover clock failure, region request failure, register mapping, unregister/remove region release, and non-waiting read latency expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/nomadik-rng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/npcm-rng.c -->
# sources/distributed-fs/ceph-client/drivers/char/hw_random/npcm-rng.c

Purpose: platform hwrng driver for Nuvoton NPCM RNG variants.

Important APIs, types, and functions: `struct npcm_rng`, `npcm_rng_init()`, `npcm_rng_cleanup()`, `npcm_rng_read()`, runtime PM callbacks, and OF matches for `nuvoton,npcm750-rng` and `nuvoton,npcm845-rng`.

Control flow: probe allocates state, maps registers, enables runtime PM, selects clock programming from match data, sets mode, and registers `hwrng`. Reads runtime-resume the device, then either poll `NPCM_RNG_DATA_VALID` or return immediately if non-waiting; each ready iteration reads one byte from `NPCM_RNGD_REG`.

State and persistence: per-device state holds base, hwrng object, device pointer, and clock-programming bits. Runtime PM suspend disables RNG while keeping clock-selection bits.

Dependencies and integration: uses platform MMIO, OF match data, `readb_poll_timeout()`, runtime PM autosuspend, and hwrng registration.

Risks and test signals: `pm_runtime_get_sync()` return is ignored in read, so PM failures may be masked. Tests should validate timeout path returns `-EIO` only for blocking reads with no bytes, autosuspend/resume toggles enable bits, match-data clock fields, and cleanup on registration failure/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/npcm-rng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/octeon-rng.c -->
# sources/distributed-fs/ceph-client/drivers/char/hw_random/octeon-rng.c

Purpose: Cavium Octeon RNG driver exposing RNM hardware through `hwrng`.

Important APIs, types, and functions: `struct octeon_rng`, `octeon_rng_init()`, `octeon_rng_cleanup()`, `octeon_rng_data_read()`, and `octeon_rng_probe()`.

Control flow: probe fetches two memory resources, maps control/status and result registers, copies a local `hwrng` template into per-device state, and registers it. Init writes RNM control bits to enable entropy and RNG; cleanup writes zero; data reads one 32-bit value from the result CSR and returns 4 bytes.

State and persistence: per-device state stores the hwrng ops and two mapped CSR pointers. Hardware enable state is controlled by hwrng init/cleanup and is not persisted.

Dependencies and integration: depends on Octeon architecture headers (`cvmx_*`), platform memory resources, devm allocation/mapping, and hwrng core.

Risks and test signals: probe maps fixed 64-bit CSR windows and returns `-ENOENT` for several distinct failures. Tests should cover missing resources, mapping failures, hwrng registration failure, init/cleanup CSR writes, and repeated reads while enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/octeon-rng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/omap-rng.c -->
# sources/distributed-fs/ceph-client/drivers/char/hw_random/omap-rng.c

Purpose: TI OMAP and Inside Secure EIP76 RNG platform driver with support for multiple register layouts and health-recovery IRQs.

Important APIs, types, and functions: `struct omap_rng_dev`, `struct omap_rng_pdata`, register maps, `omap_rng_do_read()`, `omap2_rng_init()`, `omap4_rng_init()`, `eip76_rng_init()`, `omap4_rng_irq()`, probe/remove, and PM callbacks.

Control flow: probe maps registers, enables runtime PM and optional clocks, selects pdata from OF or legacy fallback, requests IRQ for OMAP4/EIP76, then registers hwrng. Reads require a full hardware output block, poll `data_present` up to 100 iterations, copy output registers, and acknowledge ready. OMAP4/EIP76 init programs refill cycles, FRO enable/detune, thresholds, interrupts, and TRNG enable.

State and persistence: state is per-device base, clocks, pdata, and hwrng. Suspend/remove disables TRNG and runtime PM; EIP76/OMAP4 IRQ handler can recover stopped FROs by detuning and reenabling them.

Dependencies and integration: platform/OF, clocks, runtime PM, interrupt subsystem, raw MMIO, and hwrng.

Risks and test signals: register-map zero entries are used as feature tests, so incorrect maps can suppress IRQ ack or masks. Tests should cover all compatible strings, timeout/non-waiting reads, IRQ FRO recovery, PM suspend/resume, error unwinding with clocks, and EIP76 16-byte output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/omap-rng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/omap3-rom-rng.c -->
# sources/distributed-fs/ceph-client/drivers/char/hw_random/omap3-rom-rng.c

Purpose: Nokia N900/OMAP3 ROM RNG wrapper that obtains random data by calling platform ROM code.

Important APIs, types, and functions: `struct omap_rom_rng`, `omap3_rom_rng_read()`, runtime suspend/resume handlers, `omap_rom_rng_finish()`, and `omap3_rom_rng_probe()`.

Control flow: probe obtains the hwrng read function from OF match data, platform ROM callback from `platform_data`, clock `ick`, enables runtime PM autosuspend, registers cleanup action, and registers hwrng. Read runtime-resumes, passes the physical address of the caller buffer to ROM with `RNG_GEN_HW`, returns 4 bytes on success, then autosuspends. Runtime resume enables the clock and initializes ROM RNG; suspend resets ROM RNG and disables the clock.

State and persistence: per-device state stores clock, device, hwrng ops, and ROM callback. No persistent state beyond PM configuration.

Dependencies and integration: platform data callback is mandatory, OF match supplies read method, uses runtime PM, clock framework, physical address conversion, and hwrng.

Risks and test signals: `virt_to_phys(data)` assumes a directly mapped kernel buffer suitable for ROM DMA/write. Tests should cover missing callback/match data, clock failures, ROM init/reset failure logging, runtime PM read error path, and autosuspend cleanup action.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/omap3-rom-rng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/optee-rng.c -->
# sources/distributed-fs/ceph-client/drivers/char/hw_random/optee-rng.c

Purpose: OP-TEE trusted application RNG driver that bridges the Linux hwrng core to a TEE RNG TA.

Important APIs, types, and functions: `struct optee_rng_private`, global `pvt_data`, `get_optee_rng_data()`, `optee_rng_read()`, `optee_rng_init()`, `optee_rng_cleanup()`, `get_optee_rng_info()`, and TEE client probe/remove.

Control flow: probe opens an OP-TEE context, opens a session using the device UUID, queries data rate and quality, registers hwrng, and stores the device pointer. hwrng init allocates a shared memory buffer. Reads cap requests at 4 KiB, invoke `TA_CMD_GET_ENTROPY` with shared memory, copy returned bytes, and optionally sleep once based on reported data rate.

State and persistence: global singleton state stores TEE context/session, data rate, shared memory pool, quality, and hwrng object. Remove closes session/context; hwrng cleanup frees shared memory.

Dependencies and integration: TEE client bus, OP-TEE implementation matching, shared memory APIs, UUID matching, and hwrng core.

Risks and test signals: singleton state limits multi-device safety; `pvt_data.dev` is assigned after registration, so early init/read error logging may see NULL if ordering changes. Tests should cover TA errors including health-test failure, shared memory allocation/free, session open unwind, max request capping, wait timing, and remove while hwrng is registered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/optee-rng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/pasemi-rng.c -->
# sources/distributed-fs/ceph-client/drivers/char/hw_random/pasemi-rng.c

Purpose: PA Semi PWRficient on-chip RNG driver.

Important APIs, types, and functions: global `pasemi_rng`, `pasemi_rng_init()`, `pasemi_rng_cleanup()`, `pasemi_rng_data_present()`, `pasemi_rng_data_read()`, and `rng_probe()`.

Control flow: probe maps the platform resource, stores the base in the global hwrng, and registers it. Init resets/selects the raw random generator source and key size. Data-present polls the valid-count field up to 20 times with 10 microsecond delays. Data-read reads the value register. Cleanup clears random-generator enables.

State and persistence: global hwrng state contains the MMIO base in `priv`; hardware state is enable bits in the control register. No persistence.

Dependencies and integration: platform OF matching, little-endian MMIO helpers, delay loops, and hwrng core.

Risks and test signals: global state is not multi-instance safe and `data_read()` trusts `data_present()` sequencing. Tests should cover control-register programming, valid-count polling with and without wait, cleanup clearing both RNG sources, OF aliases, and mapping/registration failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/pasemi-rng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/pic32-rng.c -->
# sources/distributed-fs/ceph-client/drivers/char/hw_random/pic32-rng.c

Purpose: Microchip PIC32 RNG driver exposing enhanced TRNG mode through hwrng.

Important APIs, types, and functions: `struct pic32_rng`, `pic32_rng_init()`, `pic32_rng_read()`, `pic32_rng_cleanup()`, and `pic32_rng_probe()`.

Control flow: probe allocates state, maps MMIO, enables clock, fills hwrng hooks, and registers. Init writes `TRNGEN | TRNGMOD`. Read polls `RNGRCNT` until 64 bits are available, reads seed registers as a 64-bit sample, and returns 8 bytes; if not ready it loops only for blocking reads and otherwise returns `-EIO`. Cleanup disables `RNGCON`.

State and persistence: per-device base pointer and hwrng object; hardware enable state lives in `RNGCON`.

Dependencies and integration: platform/OF matching, clock framework, MMIO, and hwrng core.

Risks and test signals: read casts `buf` to `u64 *`, so alignment and `max >= 8` assumptions depend on hwrng core. Tests should cover non-waiting unavailable data, timeout behavior, clock failures, init/cleanup writes, and seed register ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/pic32-rng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/powernv-rng.c -->
# sources/distributed-fs/ceph-client/drivers/char/hw_random/powernv-rng.c

Purpose: bare-metal PowerNV hwrng driver for IBM POWER7+ and newer systems.

Important APIs, types, and functions: global `powernv_hwrng`, `powernv_rng_read()`, `powernv_rng_probe()`, and OF match `ibm,power-rng`.

Control flow: probe registers a single global hwrng and treats `-EEXIST` as `-ENODEV` to ignore additional matched devices. Reads compute how many native `unsigned long` values fit in the requested buffer and call `pnv_get_random_long()` for each.

State and persistence: no per-device state beyond the global hwrng. Hardware/firmware state is outside the driver.

Dependencies and integration: PowerNV arch random API, platform OF device, and hwrng core.

Risks and test signals: `powernv_rng_read()` returns 0 if `max < sizeof(unsigned long)` and assumes hwrng buffers are at least word-sized. Tests should cover duplicate device registration, small buffer handling, proper byte count, and absence of explicit wait semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/powernv-rng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/pseries-rng.c -->
# sources/distributed-fs/ceph-client/drivers/char/hw_random/pseries-rng.c

Purpose: IBM pSeries VIO hwrng driver backed by the `H_RANDOM` hypervisor call.

Important APIs, types, and functions: `pseries_rng_read()`, `pseries_rng_get_desired_dma()`, global `pseries_rng`, VIO probe/remove, and module init/exit.

Control flow: module init registers a VIO driver. Probe registers the global hwrng. Reads call `plpar_hcall(H_RANDOM)`, copy 8 bytes on success, and return `-EIO` with ratelimited logging on failure. Remove unregisters hwrng; exit unregisters the VIO driver.

State and persistence: global hwrng only; no driver-private persistent state. DMA desired size is always zero for CMO environments.

Dependencies and integration: pSeries VIO bus, POWER hypervisor call ABI, hwrng core, and module init/exit.

Risks and test signals: global hwrng is not multi-instance safe, though VIO match likely exposes one RNG. Tests should cover H_RANDOM failure, probe/remove registration pairing, CMO callback returning zero, and fixed 8-byte response semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/pseries-rng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/rockchip-rng.c -->
# sources/distributed-fs/ceph-client/drivers/char/hw_random/rockchip-rng.c

Purpose: Rockchip TRNG/RKRNG driver supporting RK3568, RK3576/RK3562/RK3528-style RKRNG, and RK3588 TRNGv1 blocks.

Important APIs, types, and functions: `struct rk_rng`, `struct rk_rng_soc_data`, SoC init/read/cleanup callbacks, `rk_rng_probe()`, runtime PM callbacks, and OF match data.

Control flow: probe maps registers, gets all clocks, applies required or optional resets, configures per-SoC hwrng callbacks/quality, enables runtime PM autosuspend, and registers hwrng. Reads runtime-resume, trigger generation according to SoC, poll ready/status bits, copy up to 32 bytes, clear status/control, and autosuspend.

State and persistence: per-device state stores clock bulk, base, SoC data, and device. Runtime PM init/cleanup owns clock enablement and block programming; RK3588 also configures auto-reseed.

Dependencies and integration: platform/OF, bulk clocks, reset controls, runtime PM, MMIO polling, and hwrng.

Risks and test signals: read paths ignore `wait` and always poll up to timeout; RK3576 uses RK3588 cleanup, intentionally clock-only. Tests should cover each compatible, reset optional vs required, version mismatch, timeout paths, autosuspend resume/suspend, max read length, and status clear behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/rockchip-rng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/s390-trng.c -->
# sources/distributed-fs/ceph-client/drivers/char/hw_random/s390-trng.c

Purpose: s390 CPACF TRNG driver providing both `/dev/trng` misc device and `hwrng` source.

Important APIs, types, and functions: `trng_read()`, sysfs `byte_counter`, `trng_hwrng_data_read()`, `trng_hwrng_read()`, debug init/exit, `trng_init()`, and `trng_exit()`.

Control flow: CPU-feature matched init registers debug support, verifies CPACF `PRNO TRNG`, registers misc device, then hwrng. Misc reads allocate a page for large reads, loop pagewise calling `cpacf_trng()`, handle scheduling/signals, copy to userspace, and update byte counters. hwrng reads cap to one page and update a separate counter.

State and persistence: global atomics count bytes served via misc and hwrng; `s390_arch_random_counter` is included in sysfs total. Debug feature state is global and removed on exit.

Dependencies and integration: s390 CPACF, CPU feature matching, miscdevice, debugfs/debug feature, sysfs attributes, hwrng, userspace copy helpers.

Risks and test signals: misc reads can be long-running and signal-interruptible; hwrng quality is implied high but not explicitly assigned here. Tests should cover missing CPACF function, misc/hwrng registration unwind, byte counters, large reads, signal interruption, copy fault, and module exit cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/s390-trng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/st-rng.c -->
# sources/distributed-fs/ceph-client/drivers/char/hw_random/st-rng.c

Purpose: STMicroelectronics platform RNG driver for a FIFO-based 16-bit sample generator.

Important APIs, types, and functions: `struct st_rng_data`, `st_rng_read()`, `st_rng_probe()`, OF match `st,rng`, and platform driver registration.

Control flow: probe maps MMIO, enables clock, initializes per-device hwrng ops, and registers. Read polls the status register until FIFO full or a calibrated timeout, then reads up to four 16-bit samples from the data register into the caller buffer and returns the byte count.

State and persistence: per-device state stores base and hwrng ops. Hardware FIFO readiness is transient; no persistent state.

Dependencies and integration: platform/OF, clock framework, MMIO, delays, and hwrng core.

Risks and test signals: read does not distinguish error status bits from FIFO readiness and ignores `wait`; pointer arithmetic on `void *` follows kernel extension expectations. Tests should cover timeout returning 0, partial reads for small `max`, clock/map failures, and FIFO-full read count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/st-rng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/stm32-rng.c -->
# sources/distributed-fs/ceph-client/drivers/char/hw_random/stm32-rng.c

Purpose: STM32/STM32MP RNG driver with clock limiting, health-test configuration, seed-error recovery, runtime PM, and suspend/resume state restore.

Important APIs, types, and functions: `struct stm32_rng_data`, `struct stm32_rng_config`, `struct stm32_rng_private`, `stm32_rng_read()`, seed concealment helpers, `stm32_rng_init()`, PM callbacks, and `stm32_rng_probe()`.

Control flow: probe maps registers, resets hardware if available, reads DT booleans for clock-error detection and config locking, gets clocks, enables runtime PM, and registers hwrng. Init enables clocks, clears errors, optionally programs entropy/health/noise controls under conditional reset, enables RNG, waits for data-ready, then disables clocks. Reads runtime-resume, recover seed errors, poll/read 32-bit words, handle clock errors, treat zero data as late seed error, and autosuspend.

State and persistence: per-device state includes clock/reset handles, SoC configuration, DT options, and saved PM register config. Suspend stores CR/NSCR/HTCR, resume restores with required conditional-reset sequencing.

Dependencies and integration: platform/OF, reset, bulk clocks, runtime/system PM, MMIO polling, and hwrng.

Risks and test signals: recovery retry logic can return partial data, and configuration locking may prevent later changes. Tests should cover each compatible clock count, clock divisor calculation, seed-error recovery with/without CONDRST, suspend/resume restore, timeout paths, zero-data recovery, and DT property combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/stm32-rng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/timeriomem-rng.c -->
# sources/distributed-fs/ceph-client/drivers/char/hw_random/timeriomem-rng.c

Purpose: generic hwrng driver for platforms where a fixed MMIO address yields a new 32-bit random value after a known period.

Important APIs, types, and functions: `struct timeriomem_rng_private`, `timeriomem_rng_read()`, `timeriomem_rng_trigger()`, `timeriomem_rng_probe()`, and remove.

Control flow: probe maps a 32-bit aligned resource, obtains period/quality from DT or platform data, initializes a completion and hrtimer, marks initial data present, and registers hwrng. Reads return 0 for non-waiting calls before the timer fires; blocking reads wait for completion, read one or more 32-bit words with period-based sleeps between additional words, then rearm the hrtimer.

State and persistence: per-device state tracks MMIO base, period, `present` flag, hrtimer, completion, and hwrng ops. Remove cancels the timer.

Dependencies and integration: platform data or OF properties, hrtimer/completion, MMIO, hwrng, and resource validation.

Risks and test signals: `present` is not protected by a lock, relying on hwrng serialization; period zero or very small periods could produce tight waits. Tests should cover missing period, bad resource alignment/size, nonblocking readiness, timer completion, multiword blocking reads, and remove during timer activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/timeriomem-rng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/via-rng.c -->
# sources/distributed-fs/ceph-client/drivers/char/hw_random/via-rng.c

Purpose: x86 VIA PadLock/XSTORE hardware RNG driver.

Important APIs, types, and functions: inline `xstore()`, `via_rng_data_present()`, `via_rng_data_read()`, `via_rng_init()`, global `via_rng`, module init/exit, and x86 CPU feature table.

Control flow: module init requires `X86_FEATURE_XSTORE` and registers hwrng. Init enables legacy RNG through `MSR_VIA_RNG` except newer Nano CPUs where CPUID `XSTORE_EN` is required. Data-present executes `xstore` up to 20 times using 1-byte chunk mode, stores the resulting datum in `rng->priv`, and returns availability. Data-read returns the cached byte count as one byte.

State and persistence: global hwrng; transient random datum cached in `rng->priv`; legacy hardware enable persists in MSR until changed.

Dependencies and integration: x86 CPU feature detection, PadLock alignment rules, inline assembly, MSR access, delays, and hwrng core.

Risks and test signals: `rng->priv` is used as a data cache rather than pointer, so concurrency depends on hwrng serialization. Tests should cover feature absence, Nano path, MSR enable/readback, wait/non-wait polling, and module unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/via-rng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/virtio-rng.c -->
# sources/distributed-fs/ceph-client/drivers/char/hw_random/virtio-rng.c

Purpose: virtio RNG frontend that exposes host-provided entropy through `hwrng`.

Important APIs, types, and functions: `struct virtrng_info`, `random_recv_done()`, `request_entropy()`, `copy_data()`, `virtio_read()`, `virtio_cleanup()`, common probe/remove, scan, freeze, restore, and virtio ID table.

Control flow: probe allocates per-device state and IDA index, finds the input virtqueue, marks device ready, and posts an initial input buffer. The virtio driver's `scan` callback registers hwrng. Completion callback obtains a used buffer, stores available length with release ordering, and completes waiters. Reads copy existing data, optionally wait for completion, and repost a buffer when drained. Remove/freeze marks removed, wakes waiters, unregisters hwrng if needed, resets device, deletes queues, and frees state.

State and persistence: per-device state tracks virtqueue, registration/removal flags, completion, data buffer/index/available length, and IDA index. No persistence outside virtio device lifetime.

Dependencies and integration: virtio core, scatterlists, completions, hwrng, IDA, DMA cacheline grouping, and PM freeze/restore.

Risks and test signals: synchronization relies on hwrng serialization plus release/acquire for `data_avail`; remove must wake blocking reads. Tests should cover nonblocking reads, interruptible wait, spurious callbacks, remove/freeze while waiting, restore registration ordering, IDA cleanup, and buffer repost after partial reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/virtio-rng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/xgene-rng.c -->
# sources/distributed-fs/ceph-client/drivers/char/hw_random/xgene-rng.c

Purpose: AppliedMicro/APM X-Gene SoC RNG driver with alarm interrupt recovery for health-test failures and FRO shutdowns.

Important APIs, types, and functions: `struct xgene_rng_dev`, `xgene_rng_init_internal()`, `xgene_rng_chk_overflow()`, `xgene_rng_irq_handler()`, `xgene_rng_data_present()`, `xgene_rng_data_read()`, `xgene_rng_init()`, probe/remove, and ACPI/OF match tables.

Control flow: probe maps CSR space, requests alarm IRQ, enables optional clock, stores context in a global hwrng, registers it, and enables wakeup. Init sets timer state, logs revision/options, programs refill/alarm/FRO registers, clears status, enables RNG and error masks. IRQ decodes health failures, logs, recovers FRO shutdown by detune/enable, tracks repeated failures over a minute, and clears status. Reads wait for ready then read up to four words and clear ready.

State and persistence: context holds CSR base, IRQ, revision, datum size, failure counter/timestamp, timer, and device. Timer resets failure count after 120 seconds.

Dependencies and integration: platform/ACPI/OF, interrupts, optional clock, timers, wakeup, MMIO, and hwrng.

Risks and test signals: global hwrng is not multi-instance safe; remove disables wakeup but does not explicitly delete `failure_timer`. Tests should cover IRQ recovery, repeated shutdown detection, ready polling, timer expiry, remove after timer setup, clock/IRQ failures, and wakeup setup errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/xgene-rng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/xiphera-trng.c -->
# sources/distributed-fs/ceph-client/drivers/char/hw_random/xiphera-trng.c

Purpose: Xiphera FPGA TRNG hwrng driver for `xip8001b-trng`.

Important APIs, types, and functions: `struct xiphera_trng`, `xiphera_trng_read()`, `xiphera_trng_probe()`, OF match table, and platform driver registration.

Control flow: probe maps registers, resets the TRNG, waits briefly for reset ack with one retry, releases reset, enables, zeroizes, waits for startup tests, acknowledges zeroize, and registers hwrng with quality 900. Read loops while full words fit and status is `TRNG_NEW_RAND_AVAILABLE`, reads a word, sends READ and ENABLE commands, and returns bytes read.

State and persistence: per-device mapped register base and hwrng object. Hardware startup and zeroize state are initialized at probe only.

Dependencies and integration: platform/OF, MMIO, sleeps/delays, hwrng.

Risks and test signals: read ignores `wait`, so consumers may receive 0 if data is not ready. Startup status is read multiple times and may change between checks. Tests should cover reset ack retry/failure, startup failure/no response, read-ready loop, register command ordering, and registration failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/xiphera-trng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/char/ipmi/Kconfig

Purpose: Kconfig menu defining the IPMI message handler, system interfaces, user interfaces, BMC-side interfaces, and related helpers.

Important APIs, types, and functions: symbols include `IPMI_HANDLER`, `IPMI_DEVICE_INTERFACE`, `IPMI_SI`, `IPMI_SSIF`, `IPMI_IPMB`, `IPMI_DMI_DECODE`, `IPMI_PLAT_DATA`, watchdog/poweroff options, BMC KCS/BT/SSIF choices, and `IPMB_DEVICE_INTERFACE`.

Control flow: `menuconfig IPMI_HANDLER` gates host-side IPMI features. Several options select common helpers such as `IPMI_PLAT_DATA` or `IPMI_KCS_BMC`. BMC-side KCS/BT/SSIF and IPMB device-interface options live outside the host-handler `if` block where appropriate, allowing BMC roles without the full host handler.

State and persistence: no runtime state; configuration choices persist in kernel build configuration.

Dependencies and integration: ties IPMI drivers to architecture, I2C/I2C slave, DMI, MFD, REGMAP_MMIO, SERIO, KUnit, and platform-specific dependencies.

Risks and test signals: dependency mistakes can make objects build without required subsystems or hide usable BMC interfaces. Tests should include `allmodconfig`, `randconfig`, host-only, BMC-only, I2C-less, DMI, KUnit, and architecture-specific configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/Makefile -->
# sources/distributed-fs/ceph-client/drivers/char/ipmi/Makefile

Purpose: kernel build rules for IPMI host, system-interface, BMC, and helper objects.

Important APIs, types, and functions: builds composite `ipmi_si.o` from SI core, KCS/SMIC/BT state machines, hotmod/hardcode/platform, memory I/O, and optional port I/O, PCI, LS2K, and PARISC pieces. It maps Kconfig symbols to object files for message handler, device interface, DMI/platform data, SSIF, IPMB, watchdog, poweroff, BMC KCS/BT/SSIF, and IPMB device interface.

Control flow: Kbuild conditionals add objects based on `CONFIG_*` values; `ipmi_si-y` aggregation creates the single system-interface module/built-in object.

State and persistence: no runtime state; build state is determined by Kconfig.

Dependencies and integration: depends on symbol names from `Kconfig` and source file names in this directory. It integrates host-side and BMC-side drivers into Linux char driver builds.

Risks and test signals: missing object mappings silently omit features; optional object conditionals must match source dependencies. Tests should run build matrices for host IPMI, BMC KCS/BT, IPMB, SSIF, PCI/IOPORT/no-IOPORT, and module vs built-in combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/bt-bmc.c -->
# sources/distributed-fs/ceph-client/drivers/char/ipmi/bt-bmc.c

Purpose: Aspeed BMC-side BT host interface exposed as `/dev/ipmi-bt-host` misc device for userspace IPMI handling.

Important APIs, types, and functions: `struct bt_bmc`, register helpers, file operations `bt_bmc_open/read/write/ioctl/release/poll`, IRQ handler, poll timer, `bt_bmc_probe()`, and `bt_bmc_remove()`.

Control flow: probe maps registers, registers misc device, configures IRQ or fallback polling timer, programs BT control registers, and clears BMC busy. Open is single-user via global atomic. Read waits for host-to-BMC attention, sets BMC busy, clears attention/read pointer, reads a length-prefixed message, copies it to userspace, and clears busy. Write waits until host not busy and no B2H attention, writes a response buffer, and sets B2H attention. IRQ or timer wakes waiters.

State and persistence: per-device MMIO base, IRQ/timer, wait queue, mutex, miscdev; global `open_count` serializes all instances. Hardware busy/attention bits hold transient protocol state.

Dependencies and integration: platform/OF for Aspeed compatibles, miscdevice, poll/wait queues, timers, IRQs, MMIO, and `linux/bt-bmc.h` ioctl.

Risks and test signals: global open count prevents multi-instance use; timer setup only occurs when IRQ config fails. Tests should cover IRQ and polling modes, read/write bounds, userspace copy faults, open exclusivity, busy bit transitions, ioctl SMS_ATN, and remove with active timer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/bt-bmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmb_dev_int.c -->
# sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmb_dev_int.c

Purpose: IPMB slave device interface that queues incoming IPMB requests to userspace and sends responses over I2C/SMBus.

Important APIs, types, and functions: `struct ipmb_msg`, `struct ipmb_dev`, `ipmb_read()`, `ipmb_write()`, `ipmb_slave_cb()`, checksum/header validation, `ipmb_probe()`, and `ipmb_remove()`.

Control flow: probe allocates state, registers a per-adapter misc device, records `i2c-protocol` mode, and registers an I2C slave callback. The slave callback reconstructs messages byte-by-byte, prepending responder address, validates minimum length and checksum on STOP, and queues requests under a spinlock. Reads block until a queued request exists, pop one, and copy it to userspace. Writes copy a userspace response and send via raw `i2c_transfer()` or SMBus block write with a temporary client address.

State and persistence: request assembly buffer, queue list, atomic queue length, message index, spinlock, wait queue, file mutex, protocol mode, and misc device. Queue is in memory only and capped at 256.

Dependencies and integration: I2C slave framework, miscdevice, poll, wait queues, spinlocks, SMBus/I2C transfer APIs.

Risks and test signals: queue elements are not explicitly drained on remove, and checksum validation only covers checksum1. Tests should cover malformed/truncated/overlong messages, queue saturation, blocking/nonblocking reads, poll, I2C vs SMBus writes, copy faults, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmb_dev_int.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_bt_sm.c -->
# sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_bt_sm.c

Purpose: host-side IPMI BT state machine used by `ipmi_si` to send one request at a time over a BT system interface.

Important APIs, types, and functions: `struct si_sm_data`, `enum bt_states`, `bt_init_data()`, `bt_start_transaction()`, `bt_get_result()`, `bt_event()`, `bt_detect()`, and exported `bt_smi_handlers`.

Control flow: transactions frame request bytes with BT length and sequence, then `bt_event()` advances through write start, write bytes, wait for BMC consume, wait for response attention, clear B2H, read bytes, and complete. It drains stale responses before new writes, reports SMS attention while idle, retries timeouts based on BT capabilities, can issue a soft reset during early failures, and enters `LONG_BUSY` if BMC remains busy.

State and persistence: state machine holds sequence number, write/read buffers, timeout, retry count, truncation flag, detected capabilities, and completion diversion state. No persistence beyond SI device lifetime.

Dependencies and integration: depends on `ipmi_si_sm.h` I/O callbacks, IPMI completion codes, module debug parameter, and upper SI scheduler calling `event()` with elapsed microseconds.

Risks and test signals: static debug helpers are not multi-open safe; timeout/retry behavior depends on detected capabilities and state timing. Tests should cover capability detection fallback, stale response draining, sequence mismatch, truncation, busy timeout, reset path, SMS_ATN, and all `si_sm_result` transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_bt_sm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_devintf.c -->
# sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_devintf.c

Purpose: `/dev/ipmiN` character device interface to the kernel IPMI message handler.

Important APIs, types, and functions: `struct ipmi_file_private`, receive handler, file ops (`open`, `release`, `poll`, `fasync`, `ioctl`), `handle_send_req()`, `handle_recv()`, compat ioctl helpers, SMI watcher callbacks, and module init/exit.

Control flow: open creates an IPMI user for the minor interface and initializes a receive queue. Incoming IPMI messages are queued under spinlock and wake waiters/fasync. Send ioctls copy request/address/data from userspace and call `ipmi_request_settime()`. Receive ioctls serialize dequeues with `recv_mutex`, copy address/data to userspace, optionally truncate, and put messages back on error. Init registers class, chrdev, and SMI watcher; watcher creates/destroys `ipmi%d` devices.

State and persistence: per-open user, receive queue, fasync queue, wait queue, retry defaults. Global class, major, and registered device list persist while module is loaded.

Dependencies and integration: IPMI message handler APIs, chrdev/class device model, userspace copy, compat ioctl ABI, poll/fasync, spinlocks/mutexes.

Risks and test signals: release destroys the user before draining queued messages; ordering must prevent new callbacks. Tests should cover all ioctls, compat structs, truncation and put-back on copy failure, poll/fasync wakeup, watcher add/remove, custom major handling, and module unload with registered devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_devintf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_dmi.c -->
# sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_dmi.c

Purpose: SMBIOS/DMI IPMI decoder that creates platform devices for IPMI interfaces and supplies slave-address lookup for ACPI-described SI devices.

Important APIs, types, and functions: `struct ipmi_dmi_info`, `dmi_decode_ipmi()`, `dmi_add_platform_ipmi()`, `ipmi_dmi_get_slave_addr()`, and `scan_for_dmi_ipmi()`.

Control flow: subsys init scans DMI devices of type IPMI, decodes interface type, base address, address space, register spacing, IRQ, and slave address. It builds `struct ipmi_plat_data`, records a lookup entry, and calls `ipmi_platform_add()` for SI or SSIF platform devices. SSIF decoding has special handling for broken systems that store I2C address in the slave-address field.

State and persistence: global linked list of decoded DMI interface info and an init-only counter for platform instance numbering. Entries persist for later ACPI slave-address lookup.

Dependencies and integration: DMI subsystem, platform-device IPMI helpers, `ipmi_plat_data.h`, `ipmi_dmi.h`, and SI type definitions.

Risks and test signals: no freeing path is needed for init-time data but malformed DMI can create wrong devices. Tests should cover old/new DMI lengths, KCS/SMIC/BT/SSIF type decoding, I/O vs memory address bits, invalid offset/type, zero base address, broken SSIF address fallback, and ACPI lookup matches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_dmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_dmi.h -->
# sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_dmi.h

Purpose: small IPMI DMI helper header that exposes DMI-derived slave-address lookup when DMI decoding is enabled.

Important APIs, types, and functions: includes `ipmi_si.h` for `enum si_type` and conditionally declares `ipmi_dmi_get_slave_addr()`.

Control flow: no runtime flow. Compile-time `CONFIG_IPMI_DMI_DECODE` decides whether consumers may call the lookup symbol.

State and persistence: no state in the header; state lives in `ipmi_dmi.c`'s decoded DMI list.

Dependencies and integration: used by IPMI SI/platform code needing to reconcile ACPI-described interfaces with SMBIOS slave addresses. It depends on `ipmi_si.h` declarations.

Risks and test signals: conditional declaration must stay aligned with the exported implementation and config symbol. Tests should include builds with and without `CONFIG_IPMI_DMI_DECODE`, plus users including the header through different IPMI build paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_dmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_ipmb.c -->
# sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_ipmb.c

Purpose: IPMI system-management-interface driver that sends host IPMI traffic over IPMB/I2C to a remote management controller and handles IPMB direct messages.

Important APIs, types, and functions: `struct ipmi_ipmb_dev`, `valid_ipmb()`, `ipmi_ipmb_check_msg_done()`, I2C slave callback, transmit formatting, kernel transmit thread, SMI handlers, cleanup/remove, and probe.

Control flow: probe reads BMC/retry properties, optionally creates a separate slave I2C client, registers slave callback, starts a transmit kthread, and registers an IPMI SMI. The slave callback accumulates inbound bytes and validates complete messages on STOP/read. Commands are forwarded to IPMI core; matching responses complete `working_msg` and signal `got_rsp`. The transmit thread waits for queued messages, formats IPMB checksums/addresses/sequence, sends via `i2c_transfer()`, retries command timeouts, and fabricates IPMI completion responses on bus errors/timeouts or for transmitted responses.

State and persistence: per-device SMI pointer, I2C clients, ready flag, current sequence, retry settings, next/working messages, kthread semaphores, buffers, receive overrun flag, and spinlock.

Dependencies and integration: I2C master/slave, IPMI SMI core, OF properties, kthreads, semaphores, spinlocks, IPMI completion codes, and `ipmb_checksum()`.

Risks and test signals: `BUG_ON(next_msg)` assumes upper layer serialization; remove/cleanup order must stop the thread and unregister slave safely. Tests should cover checksum validation, command vs response paths, sequence matching, retries/timeouts, bus errors, overrun, separate slave adapter, stop during pending message, and SMI registration failure unwind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_ipmb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_kcs_sm.c -->
# sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_kcs_sm.c

Purpose: host-side IPMI KCS state machine used by `ipmi_si` for Keyboard Controller Style system interfaces.

Important APIs, types, and functions: `struct si_sm_data`, `enum kcs_states`, `init_kcs_data()`, `start_kcs_transaction()`, `get_kcs_result()`, `kcs_event()`, `kcs_detect()`, and exported `kcs_smi_handlers`.

Control flow: a transaction starts in `KCS_START_OP`, verifies idle state, sends `KCS_WRITE_START`, writes all bytes with `KCS_WRITE_END` before the final byte, then reads bytes while hardware is in read state until idle completes. `kcs_event()` gates all states on input-buffer-free, separately waits for output-buffer-full during reads, detects attention while idle, and runs a multi-stage abort/error recovery path before retrying or marking `KCS_HOSED`.

State and persistence: state machine holds write/read buffers, positions, original write count for retries, truncation flag, error retry count, IBF/OBF timeouts, and `ERROR0` jiffies deadline. No persistence outside SI lifetime.

Dependencies and integration: `ipmi_si_sm.h` I/O callbacks, IPMI completion codes, jiffies timing, module debug parameter, and upper SI poll/interrupt scheduler.

Risks and test signals: hardware deviations are common, so error recovery and final idle-without-OBF behavior are critical. Tests should cover invalid request lengths, ATN in idle, normal write/read sequence, OBF/IBF timeout, abort recovery retry, hosed reset, truncation, bogus status 0xff detection, and scheduler return values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_kcs_sm.c -->
