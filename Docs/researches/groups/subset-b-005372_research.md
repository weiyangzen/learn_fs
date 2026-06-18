# subset-b-005372 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/smsm.c -->
# sources/distributed-fs/ceph-client/drivers/soc/qcom/smsm.c

## Purpose

`smsm.c` implements Qualcomm's Shared Memory State Machine. It exposes local shared-memory state bits through the `qcom_smem_state` provider API and converts remote shared-memory state changes into nested Linux IRQs. The mechanism is SMEM-backed: one region stores per-host state words, another stores an entry/host subscription matrix, and an optional third region reports dynamic host/entry counts.

## Important APIs, Types, and Functions

Core state is held in `struct qcom_smsm`, with per-state-word context in `struct smsm_entry` and outgoing interrupt transport in `struct smsm_host`. `smsm_update_bits()` is the exported state-provider operation. `smsm_intr()` is the threaded parent interrupt handler. `smsm_mask_irq()`, `smsm_unmask_irq()`, `smsm_set_irq_type()`, `smsm_get_irqchip_state()`, and `smsm_irq_map()` implement the child `irq_chip`/domain. Probe helpers parse mailbox channels, legacy `qcom,ipc-N` syscon triples, inbound interrupt-controller children, and optional SMEM size info.

## Control Flow

Probe reads size metadata or falls back to eight entries and three hosts, allocates host/entry arrays, identifies the child node containing `#qcom,smem-state-cells`, parses `qcom,local-host`, resolves each outgoing host transport, allocates or gets SMEM state and interrupt-mask regions, registers the local state provider, and creates IRQ domains for child nodes marked `interrupt-controller`.

State updates take a spinlock, modify the local word, issue a write memory barrier, then notify only hosts whose subscription word intersects the changed bits. Inbound interrupts read the remote state, diff it against `last_value`, and dispatch nested IRQs for enabled rising/falling bit transitions.

## State and Persistence Behavior

Persistent state is shared with remote processors in SMEM. The driver owns volatile Linux objects: IRQ domains, cached `last_value`, enabled/rising/falling bitmaps, mailbox handles, and pointers into SMEM. Masking and unmasking update the SMEM subscription matrix, so remote processors observe local interrupt interest. Remove tears down IRQ domains, mailboxes, and the `qcom_smem_state` registration, but it does not erase shared state words.

## Dependencies and Integration Points

The driver depends on Qualcomm SMEM, `qcom_smem_state`, mailbox, legacy syscon IPC, irqdomain, threaded interrupts, device tree child-node bindings, and platform-driver probing. Consumers reference the state provider through DT, while remote processors signal inbound changes through parent IRQs.

## Risks and Edge Cases

`qcom,local-host` is read without a visible error check or clamp, so malformed DT can point outside allocated host/entry dimensions. Incoming child `reg` values are checked, but the local-host-derived SMEM pointers are not. The state/subscription memory layout assumes firmware and all processors agree on host/entry counts. `smsm_update_bits()` notifies all hosts including possibly local host if subscribed. Incoming callbacks only support edge semantics; non-edge IRQ type requests fail. Shared-memory read/write ordering relies on `wmb()` before kicks and may need platform validation against remote firmware expectations.

## Test Signals

Build-test with mailbox and legacy IPC bindings enabled. DT tests should cover absent size info, custom size info, invalid `reg`, invalid local host, mailbox fallback to syscon, and child interrupt domains. Runtime tests should toggle state bits, verify remote kicks only for subscribed bits, verify nested IRQ delivery for rising and falling edges, verify mask/unmask writes subscription entries, and exercise removal after child IRQ setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/smsm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/socinfo.c -->
# sources/distributed-fs/ceph-client/drivers/soc/qcom/socinfo.c

## Purpose

`socinfo.c` registers Qualcomm SoC identity from the SMEM hardware/software build-id record. It maps Qualcomm numeric IDs to marketing names, publishes a `soc_device`, feeds SMEM identity bytes into the randomness pool, and optionally creates debugfs files for raw socinfo fields, PMIC metadata, and image-version strings.

## Important APIs, Types, and Functions

`struct qcom_socinfo` stores the registered `soc_device`, attributes, and optional debugfs root. `struct soc_id` and the large `soc_id[]` table map `QCOM_ID_*` values to names. `socinfo_machine()` performs lookup. `qcom_socinfo_probe()` reads `SMEM_HW_SW_BUILD_ID`, fills `soc_device_attribute`, registers it, initializes debugfs, and calls `add_device_randomness()`. Debugfs helpers include `qcom_show_build_id()`, PMIC model/die revision readers, image-version file operations, and `socinfo_debugfs_init()/exit()`.

## Control Flow

Probe obtains the SMEM record and its size. It builds `family = "Snapdragon"`, `machine` from the ID table, decimal `soc_id`, major/minor `revision`, and optional serial number when the SMEM item is large enough. After `soc_device_register()`, debugfs initialization decodes fields by `fmt` version using fallthrough cases. Image-version directories are backed by SMEM version tables 469 and 667.

## State and Persistence Behavior

The driver has no file persistence. It snapshots pointers and formatted strings for soc-bus registration while the authoritative data remains in SMEM. Debugfs exposes raw or decoded SMEM fields read through the original SMEM buffer and cached converted values. Remove unregisters the `soc_device` and removes debugfs recursively.

## Dependencies and Integration Points

It integrates with Qualcomm SMEM, `linux/soc/qcom/socinfo.h`, dt-binding Qualcomm IDs, the generic soc bus, debugfs, seq_file, and the kernel entropy pool. User space observes results through `/sys/devices/soc*` and optional `/sys/kernel/debug/qcom_socinfo`.

## Risks and Edge Cases

The ID table must be kept synchronized with `dt-bindings/arm/qcom,ids.h`; missing entries produce a numeric `soc_id` but no machine string. Debugfs field decoding is heavily version-dependent and relies on SMEM item sizes for only selected variable-offset fields. The image-version loop creates entries if SMEM table pointers exist but does not validate every indexed block against the returned table size. `qcom_show_build_id()` prints firmware-provided bytes as a C string, relying on SMEM layout correctness.

## Test Signals

Test with old and new socinfo formats, unknown IDs, absent serial fields, malformed PMIC array offsets, and both image-version SMEM tables. Verify soc-bus attributes, debugfs fields by format version, PMIC model fallback for unknown IDs, remove cleanup, and entropy feed path under KASAN/KMSAN for bounds issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/socinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/spm.c -->
# sources/distributed-fs/ceph-client/drivers/soc/qcom/spm.c

## Purpose

`spm.c` programs Qualcomm SAW/SPM low-power sequencers for supported CPU and L2 power controllers. It writes SoC-specific micro-sequences and control registers, exposes `spm_set_low_power_mode()` for idle code, and optionally registers a CPU-affine voltage regulator for SPM v1.1.

## Important APIs, Types, and Functions

`enum spm_reg` indexes logical registers whose physical offsets vary by hardware version. `struct spm_reg_data` stores register offsets, configuration words, PMIC/AVS fields, sequencer bytes, sleep-mode start indexes, and optional regulator data. `struct spm_driver_data` stores MMIO base and selected table. Important functions are `spm_register_write()`, `spm_register_write_sync()`, `spm_set_low_power_mode()`, `smp_set_vdd_v1_1()`, `spm_register_regulator()`, `spm_get_cpu()`, and `spm_dev_probe()`.

## Control Flow

Probe selects match data from compatible strings, maps the resource, copies the sequence table into `SPM_REG_SEQ_ENTRY`, then writes AVS, CFG, delay, PMIC, and default standby-mode control registers. If regulator support is enabled and the table supplies `set_vdd`, the driver finds the CPU whose DT node references this SAW node, initializes voltage selector state, executes the first voltage write on that CPU, and registers a regulator.

## State and Persistence Behavior

SPM hardware retains the programmed sequencer and control register state until reset or later writes. Driver state is per-device and devm-managed. Regulator state tracks `volt_sel` in memory, but actual voltage programming is stored in SAW/PMIC-related registers. `spm_set_low_power_mode()` mutates the sequencer start index in SPM control state.

## Dependencies and Integration Points

The file depends on platform MMIO, OF match tables, `soc/qcom/spm.h` sleep modes, SMP cross-calls, regulator framework, bitfield helpers, and relaxed I/O. It is registered by `arch_initcall()` so idle and cpufreq-related users can find programmed SPM state early.

## Risks and Edge Cases

Register offset tables contain zero for unsupported registers, so callers must avoid reads of absent registers; `spm_register_read()` itself does not guard missing offsets. Sequence copying always copies 64 bytes divided as words; sequence table alignment and endian assumptions matter. Voltage writes are CPU-affine and can fail if the CPU mapping is missing or offline. `smp_set_vdd_v1_1()` polls for the target level for only 200 microseconds and then re-enables AVS even on timeout. Initial-voltage selector calculation has legacy and linear-range paths that must stay consistent.

## Test Signals

Build and boot on each compatible family. Verify programmed sequence bytes, default standby selection, SPC selection through idle code, regulator registration only for v1.1 CPU SAW nodes, voltage transitions on the target CPU, AVS disable/re-enable behavior, and timeout logging. Fault tests should cover missing `qcom,saw` phandles, invalid compatible data, absent sequence offset, and regulator disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/spm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/trace-aoss.h -->
# sources/distributed-fs/ceph-client/drivers/soc/qcom/trace-aoss.h

## Purpose

`trace-aoss.h` defines tracepoints for Qualcomm AOSS message transactions. It is a trace header rather than executable driver logic and lets AOSS code record outgoing messages and their completion status.

## Important APIs, Types, and Functions

The header sets `TRACE_SYSTEM` to `qcom_aoss` and declares two `TRACE_EVENT`s: `aoss_send(const char *msg)` and `aoss_send_done(const char *msg, int ret)`. Both store the message string with `__string`; completion also stores an integer result. `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` point trace generation back to this header.

## Control Flow

Including code calls the generated `trace_aoss_send()` before sending a message and `trace_aoss_send_done()` after the operation completes. The trace subsystem expands the macros into static tracepoint definitions where `CREATE_TRACE_POINTS` is set.

## State and Persistence Behavior

No driver state is stored here. Trace records are transient ftrace/perf events controlled by tracing infrastructure and persist only in active trace buffers.

## Dependencies and Integration Points

It depends on `<linux/tracepoint.h>` and the kernel trace event build machinery. Integration is compile-time: the include path and file name must match how the AOSS implementation includes the trace header.

## Risks and Edge Cases

Trace headers are sensitive to include guards, `TRACE_HEADER_MULTI_READ`, and `TRACE_INCLUDE_PATH`; moving the file without updating these macros breaks generated trace code. Message strings must be valid at trace assignment time.

## Test Signals

Build with tracing enabled and ensure trace events appear under `events/qcom_aoss`. Exercise successful and failing AOSS sends and verify printed message/result fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/trace-aoss.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/trace-rpmh.h -->
# sources/distributed-fs/ceph-client/drivers/soc/qcom/trace-rpmh.h

## Purpose

`trace-rpmh.h` defines tracepoints for Qualcomm RPMh TCS command transmission and acknowledgment. It captures command address/data, TCS slot, message header, RPMh state, and completion wait flag for low-level power-resource debugging.

## Important APIs, Types, and Functions

The header includes `rpmh-internal.h` for `struct rsc_drv`, `struct tcs_request`, `struct tcs_cmd`, and `enum rpmh_state`. It declares `rpmh_tx_done(struct rsc_drv *d, int m, const struct tcs_request *r)` and `rpmh_send_msg(struct rsc_drv *d, int m, enum rpmh_state state, int n, u32 h, const struct tcs_cmd *c)`.

## Control Flow

RPMh code emits `rpmh_send_msg` while programming a TCS command and `rpmh_tx_done` when an ACK arrives. The trace event copies only the first command's address/data for the done path and one command pointer for the send path.

## State and Persistence Behavior

The file stores no state. Trace payloads are transient records in ftrace/perf buffers and reflect the RPMh request state at trace-call time.

## Dependencies and Integration Points

It integrates tightly with internal RPMh data structures and the trace event generator. The symbolic state printer maps sleep, wake-only, and active-only state enum values to readable strings.

## Risks and Edge Cases

The tracepoints dereference `r->cmds[0]` and `c`, so callers must pass non-empty requests and valid command pointers. Structure changes in `rpmh-internal.h` can silently break trace semantics. Include-path assumptions require the header to remain alongside RPMh sources.

## Test Signals

Build with RPMh tracing enabled. Generate active, wake-only, and sleep requests, then verify trace output for resource driver name, TCS index, command index, header, address, data, and wait flag. Include tests for multi-command requests to confirm intended first-command reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/trace-rpmh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/trace-smp2p.h -->
# sources/distributed-fs/ceph-client/drivers/soc/qcom/trace-smp2p.h

## Purpose

`trace-smp2p.h` defines tracepoints for Qualcomm SMP2P shared-memory peer state negotiation, inbound notifications, SSR acknowledgments, and outbound bit updates.

## Important APIs, Types, and Functions

It sets `TRACE_SYSTEM` to `qcom_smp2p` and declares `smp2p_ssr_ack()`, `smp2p_negotiate()`, `smp2p_notify_in()`, and `smp2p_update_bits()`. The latter two take `struct smp2p_entry *` and use fields such as `smp2p_entry->smp2p->dev` and `smp2p_entry->name`.

## Control Flow

The SMP2P implementation calls these generated trace functions around feature negotiation, incoming status updates, outgoing value changes, and subsystem-restart acknowledgment handling. The tracepoint fast paths copy device/client names and status/value fields.

## State and Persistence Behavior

No persistent state is defined. Events are emitted only when tracing is enabled and live in tracing buffers.

## Dependencies and Integration Points

The header depends on tracepoint infrastructure and the private SMP2P structures being visible at include time. `SMP2P_FEATURE_SSR_ACK` is used in flag printing, so the provider must define it before expansion.

## Risks and Edge Cases

The trace macros dereference nested SMP2P pointers, so callers must not trace after entry teardown. Private-structure coupling means refactors of SMP2P internals require matching trace header updates. Include guard and path macros must remain exact for trace generation.

## Test Signals

Build the SMP2P driver with tracing. Exercise SSR ACK negotiation, inbound remote writes, and local `update_bits()` calls, then verify event fields and flag decoding under `/sys/kernel/tracing/events/qcom_smp2p`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/trace-smp2p.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/trace_icc-bwmon.h -->
# sources/distributed-fs/ceph-client/drivers/soc/qcom/trace_icc-bwmon.h

## Purpose

`trace_icc-bwmon.h` provides a single tracepoint for Qualcomm interconnect bandwidth monitor updates. It records the monitored node name, measured bandwidth, and computed up/down thresholds.

## Important APIs, Types, and Functions

The `qcom_bwmon_update(const char *name, unsigned int meas_kbps, unsigned int up_kbps, unsigned int down_kbps)` trace event stores a string name and three unsigned bandwidth values. `TRACE_INCLUDE_PATH` is set to the driver-relative qcom path and `TRACE_INCLUDE_FILE` uses the underscore/hyphen file name.

## Control Flow

The bandwidth monitor driver calls the generated trace function whenever it recalculates or applies bandwidth thresholds. The tracepoint copies values into the trace entry and formats them as kilobits per second.

## State and Persistence Behavior

The header has no runtime state beyond trace buffers controlled by the kernel tracing subsystem.

## Dependencies and Integration Points

It depends on `<linux/tracepoint.h>` and the trace event generator. It integrates with the Qualcomm ICC BWMON driver and with ftrace/perf user-space tooling.

## Risks and Edge Cases

The nonstandard include file name `trace_icc-bwmon` and relative include path are easy to break when moving files. Callers should pass stable names during trace assignment.

## Test Signals

Enable the `icc_bwmon/qcom_bwmon_update` trace event, trigger bandwidth threshold updates, and confirm measured/up/down values match the driver's calculations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/trace_icc-bwmon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/ubwc_config.c -->
# sources/distributed-fs/ceph-client/drivers/soc/qcom/ubwc_config.c

## Purpose

`ubwc_config.c` is a Qualcomm UBWC capability database. It maps machine-compatible strings to `struct qcom_ubwc_cfg_data` records describing encoder/decoder versions, swizzle mode, bank spreading, highest bank bit, and macrotile support for display, GPU, video, and other consumers.

## Important APIs, Types, and Functions

The file defines many static `qcom_ubwc_cfg_data` constants, including no-UBWC fallback data and per-SoC families from older MSM parts through SM8750. The sole exported API is `qcom_ubwc_config_get_data()`, which calls `of_machine_get_match_data(qcom_ubwc_configs)` and returns either a data pointer or `ERR_PTR(-EINVAL)`.

## Control Flow

There is no probe. Consumers call the exported helper at runtime. OF machine matching scans `qcom_ubwc_configs`, selects the first compatible match in the root compatible list, and returns its `.data`. The module exports the symbol for other Qualcomm drivers.

## State and Persistence Behavior

All state is immutable static data. There is no hardware programming, persistence, or allocation. Consumers interpret the returned pointer directly.

## Dependencies and Integration Points

It depends on OF machine matching and `<linux/soc/qcom/ubwc.h>` definitions. Integration points are downstream display/media/GPU/interconnect code that must use the same UBWC version and memory-layout parameters for a given SoC.

## Risks and Edge Cases

The table is policy-critical: wrong `highest_bank_bit`, swizzle, or UBWC version can produce corruption rather than a clean failure. Several entries carry TODO comments for LPDDR4 bank-bit differences, indicating board/memory-configuration sensitivity not modeled by a single SoC-compatible key. `sm8750_data` uses a literal swizzle value `6` rather than named flags. Missing machine matches return an error after logging.

## Test Signals

Unit-style tests can validate every known root compatible maps to expected data. Hardware validation should exercise display/video/GPU UBWC surfaces on each SoC/memory variant, especially entries with TODO bank-bit notes and SoCs sharing another SoC's config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/ubwc_config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/wcnss_ctrl.c -->
# sources/distributed-fs/ceph-client/drivers/soc/qcom/wcnss_ctrl.c

## Purpose

`wcnss_ctrl.c` is an RPMSG control driver for Qualcomm WCNSS. It requests firmware version information, downloads the WLAN NV binary to the remote processor in fragments, waits for optional cold-boot completion, populates child devices, and exports an API for creating additional WCNSS RPMSG endpoints.

## Important APIs, Types, and Functions

`struct wcnss_ctrl` stores the RPMSG endpoint, completions, last ACK status, and async probe work. Packed message types model common headers, version responses, NV download requests, and NV download responses. Key functions are `wcnss_ctrl_smd_callback()`, `wcnss_request_version()`, `wcnss_download_nv()`, exported `qcom_wcnss_open_channel()`, `wcnss_async_probe()`, `wcnss_ctrl_probe()`, and `wcnss_ctrl_remove()`.

## Control Flow

Probe allocates state, initializes completions/work, stores drvdata, and schedules async work. The worker sends a version request and waits, loads `firmware-name` or the default NV file, fragments it into 3072-byte messages, waits for a download ACK, optionally waits for cold-boot-complete, then populates child platform devices. The RPMSG callback completes the relevant wait depending on incoming message type.

## State and Persistence Behavior

Runtime state is per RPMSG device. Firmware data is file-backed externally but only streamed; no driver-side persistence exists. Successful download changes remote WCNSS state. Remove cancels work and depopulates children.

## Dependencies and Integration Points

The file depends on RPMSG/SMD, firmware loader, OF platform population, completions, workqueues, and `linux/soc/qcom/wcnss_ctrl.h`. Other WCNSS child drivers call `qcom_wcnss_open_channel()` using this control object.

## Risks and Edge Cases

The callback dereferences `hdr->type` before verifying `count >= sizeof(*hdr)`. `wcnss_download_nv()` leaks the firmware reference if `kzalloc_flex()` fails after `request_firmware()`. Reused completions are not reinitialized before each request; current sequencing is serial but stale completions would be dangerous if retries are added. Pointer arithmetic on `const void *data` relies on compiler extensions. Fragment length uses `ssize_t left`; zero-length firmware would produce an empty last packet only if loop semantics are revisited.

## Test Signals

Test normal boot, missing firmware, custom firmware name, multi-fragment and single-fragment downloads, cold-boot and done-boot ACKs, malformed short RPMSG packets, invalid response sizes, timeout paths, remove while work is active, and endpoint creation by child drivers. Use leak detection on the allocation-failure path after firmware load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/wcnss_ctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/renesas/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/soc/renesas/Kconfig

## Purpose

This Kconfig file defines Renesas SoC-driver support, SoC-family selectors, per-SoC architecture options, and enable switches for the Renesas SoC identification, reset, power, IRQ mux, and RZ system-controller drivers in this group.

## Important APIs, Types, and Functions

The top-level `SOC_RENESAS` menu selects `GPIOLIB`, `PINCTRL`, and `SOC_BUS` for Renesas builds. Family symbols such as `ARCH_RCAR_GEN*`, `ARCH_RMOBILE`, `ARCH_RZG2L`, and `ARCH_RZN1` aggregate subsystem selections. Per-SoC symbols select family support and SoC-specific SYSC symbols. Driver symbols include `PWC_RZV2M`, `RST_RCAR`, `RZN1_IRQMUX`, `SYSC_RZ`, `SYSC_R9A08G045`, `SYSC_R9A08G046`, `SYS_R9A09G047`, `SYS_R9A09G056`, and `SYS_R9A09G057`.

## Control Flow

Kconfig selection controls build inclusion and transitive dependency setup. ARM, ARM64, and RISCV subsections expose different SoC choices. Driver build symbols are selected by SoC symbols in normal Renesas builds or manually exposed under `COMPILE_TEST`.

## State and Persistence Behavior

There is no runtime state. The file persists build-time configuration choices in `.config`, which determine which source files and platform features are compiled.

## Dependencies and Integration Points

It integrates with architecture Kconfig, Renesas interrupt controller, PM domain, timer, sysc, and reset subsystems. The matching `Makefile` consumes the driver symbols defined here.

## Risks and Edge Cases

Incorrect `select` chains can silently omit required early platform code or force code into incompatible architectures. `ARCH_R9A07G043` is defined separately for ARM64 and RISCV, so dependency interactions need care. New SoCs must update Kconfig, Makefile, DT compatibles, and SoC ID tables consistently.

## Test Signals

Run `allmodconfig`, `allyesconfig`, Renesas defconfigs, and `COMPILE_TEST` on ARM, ARM64, and RISCV. Verify each SoC symbol selects the expected driver objects and no circular or unmet dependencies appear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/renesas/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/renesas/Makefile -->
# sources/distributed-fs/ceph-client/drivers/soc/renesas/Makefile

## Purpose

The Renesas SoC Makefile maps Kconfig symbols to object files and enforces build ordering for generic SoC registration before family-specific drivers.

## Important APIs, Types, and Functions

`renesas-soc.o` is built for `CONFIG_SOC_RENESAS`. SMP-only `r9a06g032-smp.o` is gated by both `CONFIG_SMP` and `CONFIG_ARCH_R9A06G032`. RZ SYSC data providers, PWC, RST, IRQMUX, and generic `rz-sysc.o` are selected by their Kconfig symbols.

## Control Flow

Kbuild evaluates object assignments from `.config`. The comment notes `renesas-soc.o` must be first because it calls `soc_device_register()`, making generic SoC identity available before later family logic.

## State and Persistence Behavior

No runtime state exists. Build output persists as selected objects/modules according to Kconfig.

## Dependencies and Integration Points

The file integrates with Renesas Kconfig and source modules in the same directory. It is also part of early platform identity ordering because `renesas-soc.o` contains an `early_initcall()`.

## Risks and Edge Cases

Adding a new RZ SYSC data file without updating this Makefile will leave compatible match entries unresolved or absent. Misordering generic identity code could affect consumers expecting soc-bus registration early.

## Test Signals

Check `make drivers/soc/renesas/` under representative configs and confirm every enabled symbol produces the intended object and no undefined references to `rz_sysc_init_data` externs occur.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/renesas/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/renesas/pwc-rzv2m.c -->
# sources/distributed-fs/ceph-client/drivers/soc/renesas/pwc-rzv2m.c

## Purpose

`pwc-rzv2m.c` drives the Renesas RZ/V2M PWC block. It exposes two write-only PWC GPIO-like outputs and optionally registers a system power-off handler that requests PWC-managed shutdown.

## Important APIs, Types, and Functions

`struct rzv2m_pwc_priv` stores MMIO base, device, gpio chip, and a software bitmap tracking the two output states because the hardware register cannot be read. GPIO callbacks are `rzv2m_pwc_gpio_set()`, `rzv2m_pwc_gpio_get()`, and `rzv2m_pwc_gpio_direction_output()`. `rzv2m_pwc_poweroff()` writes reset, clock-enable, and power-off registers.

## Control Flow

Probe maps the register resource, clears both output bits using write-enable bits 16 and 17, initializes the cached bitmap, registers the gpiochip, and if `renesas,rzv2m-pwc-power` is present registers a devm power-off handler. Power-off writes reset/clock/power-off bits, delays 150 ms, and reports failure if execution continues.

## State and Persistence Behavior

GPIO output state is cached only in `ch_en_bits`; hardware is write-only from this driver's perspective. Power-off state is hardware-side and expected not to return. No persistent storage is used.

## Dependencies and Integration Points

It depends on platform MMIO, gpiolib, firmware node GPIO discovery, and sys-off registration. Board DT decides whether the power-off handler is active.

## Risks and Edge Cases

Software cache can diverge from hardware if firmware or another agent writes PWC GPIO. `direction_output()` validates `nr > 1`, while gpiolib normally bounds offsets. Parent assignment uses `pdev->dev.parent`, which may affect GPIO device hierarchy. The power-off path cannot verify success except by not returning.

## Test Signals

Test GPIO set/get/direction for both offsets, invalid offset rejection, reset default state on probe, optional power-off registration, and power-off MMIO write sequence on hardware or emulator.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/renesas/pwc-rzv2m.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/renesas/r9a06g032-smp.c -->
# sources/distributed-fs/ceph-client/drivers/soc/renesas/r9a06g032-smp.c

## Purpose

`r9a06g032-smp.c` provides the ARM32 secondary CPU bring-up method for Renesas R9A06G032. It writes the kernel `secondary_startup` physical address to the boot release location and sends a wakeup IPI.

## Important APIs, Types, and Functions

Global `cpu_bootaddr` stores the mapped boot-address register or SRAM pen. `cpu_lock` serializes writes. `r9a06g032_smp_prepare_cpus()` reads CPU1 `cpu-release-addr`, handles 32-bit and 64-bit property encodings, and maps it. `r9a06g032_smp_boot_secondary()` writes the startup address and wakes the target. `CPU_METHOD_OF_DECLARE()` binds the method to `renesas,r9a06g032-smp`.

## Control Flow

During SMP preparation, CPU1's DT node is parsed and the release address is ioremapped. When CPU1 is brought online, the boot method writes `__pa_symbol(secondary_startup)` under spinlock and sends `arch_send_wakeup_ipi_mask()`.

## State and Persistence Behavior

The only persistent runtime state is the static mapped release pointer. The boot register or SRAM location is mutated for secondary release. There is no cleanup path because this is early boot SMP code.

## Dependencies and Integration Points

It depends on ARM SMP infrastructure, OF CPU nodes, physical symbol translation, ioremap, and bootloader-provided `cpu-release-addr` semantics.

## Risks and Edge Cases

The 64-bit `cpu-release-addr` path truncates into `u32 bootaddr`; this matches 32-bit platforms but should be reviewed for high SRAM/register addresses. `ioremap()` failure is not explicitly logged beyond leaving `cpu_bootaddr` NULL, causing later `-ENODEV`. The code assumes CPU1 exists and is the only secondary of interest.

## Test Signals

Boot SMP and non-SMP R9A06G032 configurations, verify CPU1 online, test 32-bit and 64-bit DT property encodings, and fault-inject missing/invalid release address and failed ioremap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/renesas/r9a06g032-smp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/renesas/r9a08g045-sysc.c -->
# sources/distributed-fs/ceph-client/drivers/soc/renesas/r9a08g045-sysc.c

## Purpose

This file supplies RZ/G3S-specific initialization data for the generic Renesas RZ system-controller driver. It describes SoC ID decoding and the readable/writeable register allowlist for the R9A08G045 SYSC block.

## Important APIs, Types, and Functions

`rzg3s_sysc_soc_id_init_data` defines family `RZ/G3S`, expected ID `0x85e0447`, device-ID offset `0xa04`, and revision/specific-ID masks. `rzg3s_regmap_readable_reg()` and `rzg3s_regmap_writeable_reg()` whitelist XSPI, Ethernet, PCIe, I2C/I3C, USB power-ready, and reset-resume registers. `rzg3s_sysc_init_data` exports these callbacks and `max_register`.

## Control Flow

No probe occurs here. `rz-sysc.c` references `rzg3s_sysc_init_data` from its OF match table when `CONFIG_SYSC_R9A08G045` is enabled, then uses the data for soc-bus registration and regmap access control.

## State and Persistence Behavior

The file is immutable init data. Runtime state lives in the generic RZ SYSC driver and in the hardware registers exposed through regmap.

## Dependencies and Integration Points

It depends on `rz-sysc.h`, bit masks, and the generic RZ SYSC driver. Other drivers access allowed registers through the syscon/regmap registered by `rz-sysc.c`.

## Risks and Edge Cases

An incomplete allowlist can block legitimate client access; an overly broad list can expose reserved registers to syscon users. `max_register = 0xe20` must cover all allowed registers. The SoC ID masks must match the hardware manual to avoid false mismatch failures.

## Test Signals

Boot on RZ/G3S, verify detected family/revision, successful syscon registration, allowed read/write access for each listed register, and denied access for reserved offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/renesas/r9a08g045-sysc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/renesas/r9a08g046-sysc.c -->
# sources/distributed-fs/ceph-client/drivers/soc/renesas/r9a08g046-sysc.c

## Purpose

This file provides RZ/G3L-specific data for the generic RZ system-controller driver, including SoC ID metadata and safe regmap access callbacks for the R9A08G046 SYSC block.

## Important APIs, Types, and Functions

`rzg3l_regmap_readable_reg()` and `rzg3l_regmap_writeable_reg()` enumerate accessible XSPI, Ethernet, PCIe, I2C/I3C, power-ready, and clone-channel selection registers. `rzg3l_sysc_soc_id_init_data` defines family `RZ/G3L`, ID `0x87d9447`, ID offset `0xa04`, and masks. `rzg3l_sysc_init_data` exports callbacks and `max_register = 0xe2c`.

## Control Flow

The generic `rz-sysc.c` match table uses this data when the `renesas,r9a08g046-sysc` compatible is present. Probe then validates SoC identity and registers a syscon-backed regmap with this access policy.

## State and Persistence Behavior

No mutable driver state exists in this file. It contributes static init data consumed during generic probe.

## Dependencies and Integration Points

It integrates with `CONFIG_SYSC_R9A08G046`, `rz-sysc.h`, and syscon clients needing RZ/G3L system-controller registers.

## Risks and Edge Cases

The read/write lists are manually duplicated from hardware knowledge; omissions or wrong write permissions can cause peripheral failures or unsafe reserved-register writes. `max_register` equals the highest allowed register and must remain synchronized with the allowlist.

## Test Signals

Validate SoC detection, revision formatting, syscon registration, read/write allowlist behavior, and client drivers using Ethernet, PCIe, I2C/I3C, and clone-channel registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/renesas/r9a08g046-sysc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/renesas/r9a09g047-sys.c -->
# sources/distributed-fs/ceph-client/drivers/soc/renesas/r9a09g047-sys.c

## Purpose

`r9a09g047-sys.c` supplies RZ/G3E system-controller data for the generic RZ SYSC driver. It also provides custom SoC identification logging that reports CPU/NPU configuration and warns if the CA55 PLL is not at 1.7 GHz.

## Important APIs, Types, and Functions

`rzg3e_sys_print_id()` reads `SYS_LSI_PRR` and `SYS_LSI_MODE` to determine dual/quad core state, Ethos-U55 availability, and PLL mode. `rzg3e_sys_soc_id_init_data` defines family, expected ID, ID offset `0x304`, masks, and print callback. Readable/writeable callbacks expose thermal trim, SPI map, VSP clock, Ethernet, PCIe, and ADC config registers. `rzg3e_sys_init_data` exports the full descriptor.

## Control Flow

The generic RZ SYSC probe reads ID fields, calls `rzg3e_sys_print_id()`, registers the soc device, then creates a regmap constrained by the RZ/G3E callbacks.

## State and Persistence Behavior

Static data only. Hardware state is read for identification and later exposed through syscon regmap according to the allowlist.

## Dependencies and Integration Points

It depends on `rz-sysc.h`, bitfield helpers, MMIO reads, and generic RZ SYSC. Integration points include soc-bus users and syscon clients for SPI, VSP, Ethernet, PCIe, and ADC configuration.

## Risks and Edge Cases

Feature printing assumes PRR disable bits and mode bits are stable and readable during probe. PLL warning is informational but can indicate firmware/bootloader clock misconfiguration. Manual access lists need synchronization with bindings and hardware revisions.

## Test Signals

Boot RZ/G3E variants with dual/quad and NPU configurations, validate printed identity and PLL warning, then test regmap access for every whitelisted offset and denial for reserved addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/renesas/r9a09g047-sys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/renesas/r9a09g056-sys.c -->
# sources/distributed-fs/ceph-client/drivers/soc/renesas/r9a09g056-sys.c

## Purpose

`r9a09g056-sys.c` provides RZ/V2N system-controller data and custom SoC identification for the generic RZ SYSC driver. It reports GPU, crypto, and ISP feature combinations and enforces a register allowlist.

## Important APIs, Types, and Functions

`rzv2n_sys_print_id()` reads PRR and mode registers, computes feature flags for Mali-G31, crypto engine, and Mali-C55 ISP, derives an `nNN` suffix, and warns on non-1.7 GHz CA55 PLL. `rzv2n_sys_soc_id_init_data` defines family `RZ/V2N`, ID `0x867d447`, offset `0x304`, and masks. `rzv2n_regmap_readable_reg()` and `rzv2n_regmap_writeable_reg()` expose trim, Ethernet, PCIe, and ADC registers.

## Control Flow

Generic probe uses the descriptor to validate ID, print the extended identity, and register a regmap with RZ/V2N-specific access permissions.

## State and Persistence Behavior

Only static init data exists. Probe reads immutable or strap-derived hardware ID/configuration registers; syscon clients later mutate only writeable allowlisted registers.

## Dependencies and Integration Points

The file integrates with `CONFIG_SYS_R9A09G056`, `rz-sysc.c`, soc-bus registration, and syscon users for GbE, PCIe, ADC, and trim data.

## Risks and Edge Cases

The feature suffix formula (`41 + feature_flags`) encodes product variants compactly and must match Renesas naming. Incorrect PRR/mode interpretation would misreport features. Allowlist accuracy is essential to avoid blocking clients or exposing reserved registers.

## Test Signals

Validate identity strings on RZ/V2N feature variants, PLL warning behavior, SoC mismatch rejection, and syscon read/write access matrix.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/renesas/r9a09g056-sys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/renesas/r9a09g057-sys.c -->
# sources/distributed-fs/ceph-client/drivers/soc/renesas/r9a09g057-sys.c

## Purpose

`r9a09g057-sys.c` provides RZ/V2H system-controller initialization data. It reports GPU/ISP presence, validates SoC ID, warns on CA55 PLL configuration, and defines read/write permissions for dual-PCIe-capable SYS registers.

## Important APIs, Types, and Functions

`rzv2h_sys_print_id()` reads PRR/mode registers and prints feature-specific identity. `rzv2h_sys_soc_id_init_data` describes family, ID `0x847a447`, ID offset, masks, and callback. `rzv2h_regmap_readable_reg()` and `rzv2h_regmap_writeable_reg()` list trim, Ethernet, PCIe channel 0/1, PCIe mode, and ADC config offsets. `rzv2h_sys_init_data` sets `max_register = 0x170c`.

## Control Flow

When generic `rz-sysc.c` matches `renesas,r9a09g057-sys`, it uses this data for identity and regmap setup. Client drivers then acquire the syscon regmap via the node.

## State and Persistence Behavior

No local mutable state. Hardware configuration bits are read during identification, and writeable SYS registers persist in hardware until reset or later writes.

## Dependencies and Integration Points

It depends on bitfield helpers, MMIO reads, `rz-sysc.h`, `CONFIG_SYS_R9A09G057`, and clients of Ethernet/PCIe/ADC SYS registers.

## Risks and Edge Cases

Dual PCIe channel register coverage increases allowlist maintenance risk. Feature detection assumes PRR disable-bit polarity. PLL warning may reveal boot firmware issues but does not stop probe.

## Test Signals

Boot RZ/V2H and RZ/V2H(P) boards, validate identity feature strings, PLL warning, ID mismatch handling, and read/write behavior for both PCIe channel register sets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/renesas/r9a09g057-sys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/renesas/rcar-rst.c -->
# sources/distributed-fs/ceph-client/drivers/soc/renesas/rcar-rst.c

## Purpose

`rcar-rst.c` initializes Renesas R-Car/RZ reset controller support. It reads and caches mode pins, enables watchdog-reset behavior on selected generations, and exports a helper for programming Gen3 realtime-core boot addresses.

## Important APIs, Types, and Functions

`struct rst_config` defines mode register offset plus optional `configure` and `set_rproc_boot_addr` callbacks. `rcar_rst_init()` finds a matching reset node, maps registers, stores `saved_mode`, and runs configuration. Public APIs are `rcar_rst_read_mode_pins()` and exported `rcar_rst_set_rproc_boot_addr()`. Gen-specific helpers write WDTRSTCR variants and CR7BAR.

## Control Flow

The first call to `rcar_rst_read_mode_pins()` lazily calls `rcar_rst_init()` if needed. Init matches DT compatible, maps MMIO, stores global base and boot-address callback, reads mode pins, and enables watchdog reset where required. Remoteproc boot-address calls validate 256 KiB alignment through `CR7BAR_MASK`, then write CR7BAR and enable it.

## State and Persistence Behavior

Global `rcar_rst_base`, `saved_mode`, and function pointer persist after init. `saved_mode` is `__initdata`, but the public read path uses it after init-time setup in normal early-call patterns. Hardware writes persist in reset-controller registers.

## Dependencies and Integration Points

It depends on OF address mapping, Renesas reset DT compatibles, and `linux/soc/renesas/rcar-rst.h`. Consumers include SoC setup and remoteproc code needing mode pins or CR7 boot address programming.

## Risks and Edge Cases

Global singleton design assumes one reset controller. Failure after mapping does not unmap because this is init-time infrastructure. Boot address validation rejects any low bits outside `CR7BAR_MASK`; callers must pass aligned physical addresses. New Gen4/Gen5 variants require correct modemr and watchdog behavior.

## Test Signals

Boot supported Gen1/2/3/4 and RZ/G variants, verify mode-pin values, watchdog reset enable writes, remoteproc boot address alignment rejection/acceptance, and behavior when no matching node exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/renesas/rcar-rst.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/renesas/renesas-soc.c -->
# sources/distributed-fs/ceph-client/drivers/soc/renesas/renesas-soc.c

## Purpose

`renesas-soc.c` performs early Renesas SoC identification and registers a generic `soc_device`. It maps root DT compatibles to family/name/id data, optionally reads chip ID registers, derives revision strings, checks product IDs, and logs the detected SoC.

## Important APIs, Types, and Functions

`struct renesas_family` defines family name and optional hardcoded ID register. `struct renesas_soc` ties a compatible to family and expected product ID. `renesas_socs[]` is conditionally compiled from Kconfig. `struct renesas_id` and `renesas_ids[]` describe ID register layouts. `renesas_soc_init()` is the `early_initcall()` entry point.

## Control Flow

Early init matches the root node against `renesas_socs`, derives `soc_id` from the compatible suffix, locates a chip-ID syscon node or falls back to family hardcoded PRR/CCCR address, allocates `soc_device_attribute`, reads and decodes revision if possible, checks product masks against expected ID, logs detection, and registers the soc device.

## State and Persistence Behavior

The registered `soc_device_attribute` and soc device intentionally persist. Temporary ID mappings are unmapped after read. There is no unregister path because this is early platform identity.

## Dependencies and Integration Points

It depends on OF root compatible matching, optional syscon/chip-ID MMIO nodes, bitfield helpers, and the soc bus. Many drivers and user-space tools depend indirectly on accurate soc-bus identity.

## Risks and Edge Cases

The large compatible table is Kconfig-conditional; missing Kconfig coverage prevents detection even if DT is correct. Product-ID masks differ by PRR, BSID, RZ/G2L, and RZ/V2M layouts. Special M3-W revision corrections are hardcoded. If `soc_device_register()` fails, allocations are freed; on success they persist without devm ownership.

## Test Signals

Test root-compatible detection across enabled SoCs, chip-ID fallback paths, RZ/G2L and RZ/V2M revision formats, M3-W revision quirks, product mismatch warnings, and absence of ID registers for SoCs with no expected ID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/renesas/renesas-soc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/renesas/rz-sysc.c -->
# sources/distributed-fs/ceph-client/drivers/soc/renesas/rz-sysc.c

## Purpose

`rz-sysc.c` is the generic Renesas RZ system-controller driver. It registers SoC identity from per-SoC data files and exposes the controller MMIO region as a syscon regmap with SoC-specific read/write allowlists.

## Important APIs, Types, and Functions

`struct rz_sysc` stores base and device. `rz_sysc_soc_init()` parses the compatible into a `soc_id`, reads device ID/revision fields through `rz_sysc_soc_id_init_data`, validates expected ID, prints identity, and calls `soc_device_register()`. `rz_sysc_probe()` maps MMIO, calls identity setup, creates a `regmap_config`, initializes MMIO regmap, and registers it with `of_syscon_register_regmap()`.

## Control Flow

Subsys init registers the platform driver. Probe selects match data compiled for enabled SoCs, maps resource 0, performs SoC registration, configures 32-bit/stride-4 fast regmap using callbacks from the data provider, and publishes it as syscon.

## State and Persistence Behavior

Per-device state is devm-managed, but registered `soc_device` is not paired with an unregister action in this file. Hardware SYS registers persist outside driver memory. The regmap lives for the platform device lifetime.

## Dependencies and Integration Points

It depends on `rz-sysc.h`, per-SoC descriptors, platform MMIO, regmap-mmio, syscon registration, and soc bus. Peripheral drivers access the exposed syscon by phandle.

## Risks and Edge Cases

Compatible parsing assumes a comma and hyphen exist; malformed compatible strings could produce invalid pointer arithmetic. The size cap for `soc_id` uses `strscpy()` with computed length, so off-by-one semantics need review when adding long compatibles. No `soc_device_unregister()` action means unbind is not symmetrical, though bind attrs are suppressed.

## Test Signals

Probe each supported compatible, validate soc-bus entries, ID mismatch rejection, syscon lookup by clients, regmap allowlist enforcement, and malformed/long compatible resilience under test DT overlays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/renesas/rz-sysc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/renesas/rz-sysc.h -->
# sources/distributed-fs/ceph-client/drivers/soc/renesas/rz-sysc.h

## Purpose

`rz-sysc.h` is the private interface between the generic RZ SYSC driver and per-SoC data files. It defines identity metadata, register-access callbacks, and extern descriptors for enabled RZ/G3 and RZ/V2 system controllers.

## Important APIs, Types, and Functions

`struct rz_sysc_soc_id_init_data` contains family string, expected ID, device-ID offset, revision and specific-ID masks, and optional `print_id()` callback. `struct rz_sysc_init_data` contains the identity descriptor, readable/writeable callback pointers, and maximum register offset. Externs name the descriptors implemented by the per-SoC C files.

## Control Flow

No execution occurs in the header. `rz-sysc.c` consumes the structures at probe time through its OF match table and calls optional `print_id()`.

## State and Persistence Behavior

The header declares immutable descriptor shapes. Runtime state is owned by `rz-sysc.c`; hardware state is exposed through regmap.

## Dependencies and Integration Points

It depends on device, soc-bus, and basic type declarations. It creates a narrow integration boundary for adding new RZ system-controller variants without modifying generic probe logic heavily.

## Risks and Edge Cases

Callback contracts are informal: per-SoC files must ensure allowlist callbacks and `max_register` are consistent. Extern declarations must match Kconfig/Makefile object inclusion or link failures result.

## Test Signals

Compile every `SYSC_RZ` combination, including individual SoC symbols, and verify no missing externs. Review new descriptors for ID mask, offset, max register, and callback consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/renesas/rz-sysc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/renesas/rzn1_irqmux.c -->
# sources/distributed-fs/ceph-client/drivers/soc/renesas/rzn1_irqmux.c

## Purpose

`rzn1_irqmux.c` programs the Renesas RZ/N1 GPIO interrupt multiplexer. It reads the DT `interrupt-map`, validates parent GIC SPI lines, and writes child interrupt sources into eight mux output registers.

## Important APIs, Types, and Functions

`rzn1_irqmux_parent_args_to_line_index()` validates a parent interrupt specifier and converts GIC SPI numbers 103 through 110 into output indexes 0 through 7. `rzn1_irqmux_probe()` maps registers, validates `#interrupt-cells = <1>` and `#address-cells = <0>`, iterates `of_imap_item`s, rejects duplicate outputs, and writes child hwirq values to `regs[index]`.

## Control Flow

Probe maps MMIO, validates binding shape, initializes the OF interrupt-map parser, then for each map item determines the output line and programs the mux. The driver does not register an IRQ domain; it configures static routing described by DT.

## State and Persistence Behavior

No driver-private state persists after probe except devm mapping. The programmed mux registers persist in hardware until reset or later writes.

## Dependencies and Integration Points

It depends on platform MMIO, OF interrupt-map parsing, ARM GIC binding constants, and RZ/N1 GPIO interrupt routing. It is selected by `ARCH_RZN1` when DW APB GPIO is enabled.

## Risks and Edge Cases

The code assumes register spacing matches `u32 __iomem *regs` indexing. It validates duplicate parent outputs but not whether child hwirq values are in a hardware-supported source range. Error paths manually drop `parent_args.np` for early returns inside the iterator.

## Test Signals

Use DT overlays with valid maps, duplicate outputs, invalid GIC type, out-of-range SPI numbers, wrong interrupt/address cell counts, and malformed maps. Verify programmed register values on hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/renesas/rzn1_irqmux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/rockchip/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/soc/rockchip/Kconfig

## Purpose

This Kconfig file exposes Rockchip SoC driver options for GRF default programming, IO-domain voltage selection, and DTPM hierarchy registration.

## Important APIs, Types, and Functions

`ROCKCHIP_GRF` is a bool defaulting on for `ARCH_ROCKCHIP`. `ROCKCHIP_IODOMAIN` is a tristate depending on OF. `ROCKCHIP_DTPM` is a tristate depending on `DTPM && m`, meaning it is module-oriented. The menu is visible when `ARCH_ROCKCHIP` or `COMPILE_TEST` is set.

## Control Flow

Kconfig controls which Makefile objects are built. Enabling `ROCKCHIP_GRF` compiles early GRF setup, `ROCKCHIP_IODOMAIN` compiles the regulator-notifier IO-domain driver, and `ROCKCHIP_DTPM` compiles the DTPM hierarchy module.

## State and Persistence Behavior

There is no runtime state in Kconfig. Choices persist in `.config`.

## Dependencies and Integration Points

It integrates with Rockchip architecture config, OF, DTPM, regulator, syscon, and the matching Makefile.

## Risks and Edge Cases

`ROCKCHIP_DTPM` depends on `m`, so built-in DTPM hierarchy behavior is intentionally not offered. `ROCKCHIP_IODOMAIN` lacks an explicit regulator dependency in this file and relies on broader build dependency resolution. Missing defaults could leave critical GRF setup disabled on real platforms.

## Test Signals

Run Rockchip defconfig, allmodconfig, and COMPILE_TEST builds. Verify object inclusion and dependency prompts, especially DTPM module-only behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/rockchip/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/rockchip/Makefile -->
# sources/distributed-fs/ceph-client/drivers/soc/rockchip/Makefile

## Purpose

The Rockchip SoC Makefile maps Kconfig symbols to the GRF, IO-domain, and DTPM object files.

## Important APIs, Types, and Functions

`obj-$(CONFIG_ROCKCHIP_GRF) += grf.o`, `obj-$(CONFIG_ROCKCHIP_IODOMAIN) += io-domain.o`, and `obj-$(CONFIG_ROCKCHIP_DTPM) += dtpm.o` are the entire build contract.

## Control Flow

Kbuild includes the relevant object when each symbol is enabled as built-in or module according to Kconfig type.

## State and Persistence Behavior

No runtime state. Build artifacts reflect `.config`.

## Dependencies and Integration Points

It depends on local Kconfig symbols and source file names staying synchronized.

## Risks and Edge Cases

Renaming source files or adding a new Rockchip SoC helper without this Makefile update will silently omit code from builds. Module/built-in state follows Kconfig and can affect init ordering.

## Test Signals

Build each symbol individually as supported and verify expected object/module output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/rockchip/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/rockchip/dtpm.c -->
# sources/distributed-fs/ceph-client/drivers/soc/rockchip/dtpm.c

## Purpose

`dtpm.c` registers a Rockchip RK3399 Dynamic Thermal Power Management hierarchy. It describes virtual package nodes and DT-backed CPU/GPU power nodes for power capping.

## Important APIs, Types, and Functions

`rk3399_hierarchy[]` is a `struct dtpm_node` tree with root `rk3399`, child `package`, CPU nodes `/cpus/cpu@0` through `/cpus/cpu@101`, and GPU node `/gpu@ff9a0000`. `rockchip_dtpm_match_table` binds the hierarchy to `rockchip,rk3399`. Module init/exit call `dtpm_create_hierarchy()` and `dtpm_destroy_hierarchy()`.

## Control Flow

On module load, DTPM scans the match table against the running platform and creates the hierarchy if RK3399 matches. On unload, it destroys the hierarchy.

## State and Persistence Behavior

Hierarchy nodes are static `__initdata` descriptors used to create runtime DTPM objects. Runtime state belongs to the DTPM core and is removed at module exit.

## Dependencies and Integration Points

It depends on the DTPM framework, OF matching, and availability of panfrost and cpufreq-dt providers, noted by `MODULE_SOFTDEP("pre: panfrost cpufreq-dt")`.

## Risks and Edge Cases

Hardcoded DT paths must match board DTs. The author string appears to miss a closing `>` in the module metadata. DTPM creation failure is returned directly from module init. The `depends on DTPM && m` Kconfig shape makes this module-only.

## Test Signals

Load/unload on RK3399 with cpufreq and panfrost present, inspect DTPM hierarchy, test missing GPU/CPU provider behavior, and run module metadata checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/rockchip/dtpm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/rockchip/grf.c -->
# sources/distributed-fs/ceph-client/drivers/soc/rockchip/grf.c

## Purpose

`grf.c` applies early default settings to Rockchip General Register Files. It disables problematic JTAG switching, selects PWM/clock behavior, configures weak pulls, and applies USB3 OTG quirks for selected SoCs.

## Important APIs, Types, and Functions

`struct rockchip_grf_value` describes one register write with a description, offset, and hiword-mask value. `struct rockchip_grf_info` groups arrays per compatible. Static data covers RK3036, RK3128, RK3228, RK3288, RK3328, RK3368, RK3399, RK3566, RK3576, and RK3588 GRF variants. `rockchip_grf_init()` iterates matching DT nodes, gets their syscon regmap, and writes all values.

## Control Flow

`postcore_initcall()` runs after core init. For each available matching node, it resolves the syscon regmap and writes each default value, logging failures but continuing through the array. Fatal errors occur for missing match data or unavailable syscon regmap.

## State and Persistence Behavior

The driver keeps no runtime state. It mutates GRF hardware registers early; those settings persist until reset or later writes.

## Dependencies and Integration Points

It depends on OF matching, syscon/regmap, and `FIELD_PREP_WM16_CONST()` hiword-mask semantics. It integrates with pinctrl, MMC, USB, PWM, I3C, and clock expectations by applying safe defaults.

## Risks and Edge Cases

Wrong GRF defaults can break board pinmux or peripheral routing globally. Because writes are early and unconditional for available nodes, board-specific exceptions are hard to express. Errors in individual writes are logged but do not abort, so partially applied defaults are possible.

## Test Signals

Boot each compatible SoC, read back GRF fields where readable, validate MMC/JTAG/PWM/USB/I3C behavior, and test unavailable syscon failure paths. Static checks should verify hiword-mask values target correct bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/rockchip/grf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/rockchip/io-domain.c -->
# sources/distributed-fs/ceph-client/drivers/soc/rockchip/io-domain.c

## Purpose

`io-domain.c` keeps Rockchip SoC IO-domain voltage selector bits synchronized with regulator voltages. It programs GRF/PMUGRF bits initially and through regulator notifiers so hardware IO voltage domains track external 1.8 V or 3.3 V rails.

## Important APIs, Types, and Functions

`struct rockchip_iodomain_supply` binds one regulator to an index and notifier. `struct rockchip_iodomain_soc_data` defines GRF offset, supply names, optional init, and optional write callback. `rockchip_iodomain_notify()` reacts to regulator pre/post/abort voltage events. `rockchip_iodomain_write()` handles generic hiword-mask writes; `rk3568_iodomain_write()` handles split selector registers. Per-SoC init functions switch special domains from GPIO/static control into framework control.

## Control Flow

Probe selects SoC data, resolves GRF regmap from parent syscon or legacy `rockchip,grf` phandle, then iterates up to 16 supply names. For each present regulator it reads current voltage, rejects voltages above 3.6 V, writes the selector, and registers a notifier. After all supplies, optional SoC init writes special control bits. Remove unregisters notifiers in reverse order.

## State and Persistence Behavior

Driver state stores regulator pointers and notifier blocks. GRF selector bits persist in hardware. Notifier events adjust hardware before voltage increases using the maximum requested voltage, after voltage changes, or after aborts.

## Dependencies and Integration Points

It depends on syscon/regmap, regulator consumer/notifier APIs, OF/platform probing, and Rockchip GRF bindings. It is safety-critical for pin electrical limits and peripheral operation.

## Risks and Edge Cases

The notifier must program selectors before external voltage rises; wrong event handling can overvoltage IO pads. Voltage thresholds rely on datasheet maximums and classify anything above 1.98 V as 3.3 V. Missing optional regulators are ignored, leaving bootloader defaults. `rk3568_iodomain_write()` intentionally skips some indexes, so SoC data ordering is critical. If probe fails mid-way, registered notifiers are unwound, but already-written GRF bits remain.

## Test Signals

Test initial selector programming for every supported SoC data table, regulator pre-change/commit/abort paths, too-high voltage rejection, missing optional supplies, probe deferral, notifier unregister on remove, and special init bits for PX30/RK3288/RK3308/RK3328/RK3368/RK3399.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/rockchip/io-domain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/samsung/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/soc/samsung/Kconfig

## Purpose

This Kconfig file defines Samsung SoC driver support for Exynos ChipID/ASV, USI, PMU, PM suspend memory CRC checking, and the Exynos regulator coupler.

## Important APIs, Types, and Functions

`SOC_SAMSUNG` gates the menu. `EXYNOS_CHIPID` selects MFD syscon and soc bus and selects ARM ASV helpers on ARM Exynos. `EXYNOS_USI` selects syscon and defaults on for ARM64 Exynos. `EXYNOS_PMU` selects MFD core and MMIO regmap, with `EXYNOS_PMU_ARM_DRIVERS` selected for ARM Exynos. `SAMSUNG_PM_CHECK` and chunk size configure legacy suspend CRC. `EXYNOS_REGULATOR_COUPLER` enables Exynos voltage coupling.

## Control Flow

Kconfig selections drive which Makefile objects are compiled and which architecture-specific data tables are available to generic PMU and ChipID code.

## State and Persistence Behavior

No runtime state. User or defconfig choices persist in `.config`.

## Dependencies and Integration Points

It integrates with `ARCH_EXYNOS`, COMPILE_TEST, MFD, syscon, regulator, PM, CRC32, and soc bus subsystems.

## Risks and Edge Cases

Architecture gating intentionally excludes ARMv7-only data on ARM64; mismatches can produce missing PMU data pointers. `EXYNOS_PMU` is bool, not tristate, affecting init ordering. PM_CHECK options are legacy-platform-specific and can be expensive at runtime.

## Test Signals

Run ARM and ARM64 Exynos defconfigs plus COMPILE_TEST. Verify object selection for ChipID, USI, PMU core, ARM PMU tables, regulator coupler, and PM_CHECK chunk-size prompts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/samsung/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/samsung/Makefile -->
# sources/distributed-fs/ceph-client/drivers/soc/samsung/Makefile

## Purpose

The Samsung SoC Makefile maps Exynos/Samsung Kconfig symbols to object files and multi-object modules.

## Important APIs, Types, and Functions

`exynos_chipid-y` combines `exynos-chipid.o` and `exynos-asv.o`; `exynos_pmu-y` combines `exynos-pmu.o` and `gs101-pmu.o`. ARM PMU data tables build under `CONFIG_EXYNOS_PMU_ARM_DRIVERS`. USI, regulator coupler, ASV ARM extension, and PM check objects are independently selected.

## Control Flow

Kbuild creates built-in objects or modules according to Kconfig type. Multi-object assignments ensure shared ASV and GS101 PMU code is linked with its parent module/object.

## State and Persistence Behavior

No runtime state. It controls build artifacts only.

## Dependencies and Integration Points

It depends on Kconfig symbols and local file names. Generic PMU and ChipID code depend on companion objects being linked when features are enabled.

## Risks and Edge Cases

Missing a companion object can create unresolved symbols or disabled functionality. The underscore module names (`exynos_chipid`, `exynos_pmu`) differ from source hyphen names and must match module expectations.

## Test Signals

Build each symbol combination, especially `EXYNOS_CHIPID=m`, `EXYNOS_PMU=y`, and ARM-only PMU table selections, and verify module/object contents with `nm` or build logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/samsung/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/samsung/exynos-asv.c -->
# sources/distributed-fs/ceph-client/drivers/soc/samsung/exynos-asv.c

## Purpose

`exynos-asv.c` applies Exynos Adaptive Supply Voltage data to CPU OPP tables. It selects SoC-specific ASV probing, computes adjusted voltages, updates OPP entries, and refreshes energy-model chip-binning data.

## Important APIs, Types, and Functions

`exynos_asv_init()` is called from the ChipID driver after regmap setup. It allocates `struct exynos_asv`, reads product ID, selects `exynos5422_asv_init()` for Exynos5800/5422-class ID, reads optional `samsung,asv-bin`, initializes subsystem back-pointers, and updates OPPs. `exynos_asv_update_cpu_opps()` adjusts per-frequency voltages. `exynos_asv_update_opps()` avoids duplicate work for CPUs sharing an OPP table.

## Control Flow

ChipID probe calls ASV init. If the SoC is unsupported, the function returns success with no changes. Supported SoCs wait for CPU0 OPP availability, run the SoC-specific probe to fill tables/group selection, then iterate possible CPUs and adjust each unique OPP table.

## State and Persistence Behavior

ASV state is devm-managed under the ChipID device. Updated OPP voltages persist in kernel OPP tables for runtime consumers; no nonvolatile storage is changed.

## Dependencies and Integration Points

It depends on ChipID regmap, Exynos ASV tables, CPU device nodes, OPP core, and energy model. CPUfreq and thermal scheduling observe the adjusted OPP/EM data.

## Risks and Edge Cases

Unsupported SoCs intentionally no-op. Missing OPPs are logged and skipped, so partial voltage adjustment is possible. `get_cpu_device(0)` is not null-checked before OPP count. A typo in an error message says "udate". ASV table dimensions and group indexes must be valid or inline table access can go out of bounds.

## Test Signals

Boot supported and unsupported Exynos SoCs, test OPP probe deferral, missing OPP rows, DT-provided ASV bin, updated OPP voltages, EM refresh, and shared OPP table deduplication.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/samsung/exynos-asv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/samsung/exynos-asv.h -->
# sources/distributed-fs/ceph-client/drivers/soc/samsung/exynos-asv.h

## Purpose

`exynos-asv.h` defines private data structures and helpers for Exynos Adaptive Supply Voltage support shared by ChipID, generic ASV, and SoC-specific ASV table code.

## Important APIs, Types, and Functions

`struct asv_limit_entry`, `struct exynos_asv_table`, `struct exynos_asv_subsys`, and `struct exynos_asv` model ASV limits, table dimensions, per-subsystem metadata, and global ASV selection state. Inline helpers read table entries, OPP voltages, and OPP frequencies. `exynos_asv_init()` is declared for ChipID integration.

## Control Flow

No runtime control flow exists in the header. C files fill the structures, then generic code calls inline helpers while updating OPP tables.

## State and Persistence Behavior

The header describes in-memory ASV state only. Table buffers are referenced through pointers owned by implementation code.

## Dependencies and Integration Points

It depends on `struct regmap` forward declaration and kernel integer types. It is a private interface between `exynos-asv.c`, `exynos-chipid.c`, and SoC-specific ASV implementations.

## Risks and Edge Cases

Inline table indexing has no bounds checks. Callers must ensure `num_rows`, `num_cols`, group indexes, and table buffers are valid. The fixed `subsys[2]` array limits current ASV modeling to two CPU subsystems.

## Test Signals

Compile with each ASV implementation. Unit-review table dimensions against all helper accesses and run KASAN boot tests on supported SoCs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/samsung/exynos-asv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/samsung/exynos-chipid.c -->
# sources/distributed-fs/ceph-client/drivers/soc/samsung/exynos-chipid.c

## Purpose

`exynos-chipid.c` identifies Samsung Exynos and Google GS101 SoCs, registers a `soc_device`, and invokes ASV initialization. It supports both syscon-backed ChipID registers and efuse/OTP-style MMIO.

## Important APIs, Types, and Functions

`struct exynos_chipid_variant` describes revision register layout and efuse mode. `soc_ids[]` maps product IDs to names. `exynos_chipid_get_chipid_info()` reads product and revision fields. `exynos_chipid_get_efuse_regmap()` maps resource 0 and builds a clocked MMIO regmap. `exynos_chipid_probe()` performs match-data selection, regmap setup, identity read, soc-bus registration, devm unregister action, and `exynos_asv_init()`.

## Control Flow

Probe obtains variant data from OF. Efuse variants create a local regmap; other variants use `device_node_to_regmap()`. Product/revision are decoded according to variant layout, root DT `model` is copied as machine, `soc_id` is looked up by product ID, `soc_device_register()` is called, then ASV setup is attempted.

## State and Persistence Behavior

The registered soc device persists for the platform-device lifetime and is unregistered by a devm action. ASV may mutate OPP table voltages. No hardware state is changed by identification reads.

## Dependencies and Integration Points

It depends on regmap, syscon, platform resources, soc bus, OF root model, Exynos ChipID register definitions, and `exynos-asv.c`. User space sees soc-bus identity; CPUfreq/thermal may observe ASV voltage changes.

## Risks and Edge Cases

Unknown product IDs fail probe even if raw registers are readable. Root `model` read ignores errors, so machine can be null. The efuse regmap config defines `max_register` using a local `reg_config` initializer expression; build coverage is important. ASV failure fails ChipID probe after soc-device registration, relying on devm action to unwind.

## Test Signals

Test Exynos4210, Exynos850-style, and GS101 variants; unknown product ID; regmap read failures; root model absence; module remove/unbind; ASV supported/unsupported paths; and efuse pclk handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/samsung/exynos-chipid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/samsung/exynos-pmu.c -->
# sources/distributed-fs/ceph-client/drivers/soc/samsung/exynos-pmu.c

## Purpose

`exynos-pmu.c` is the generic Samsung Exynos PMU controller driver. It provides raw PMU access helpers, programs powerdown configuration tables, creates PMU regmaps, registers child devices, and implements GS101-specific CPU hotplug/cpuidle firmware hint handling.

## Important APIs, Types, and Functions

`struct exynos_pmu_context` stores device, PMU data, PMU and interrupt-generator regmaps, raw spinlock, CPU-hotplug bitmap, and suspend/reboot flags. Public helpers include `pmu_raw_writel()`, `pmu_raw_readl()`, `exynos_sys_powerdown_conf()`, `exynos_get_pmu_regmap()`, and `exynos_get_pmu_regmap_by_phandle()`. GS101 helpers manage CPU inform and interrupt bits for online/offline paths. `exynos_pmu_probe()` sets up regmap, PMU data, CPU PM integration, MFD children, and OF children.

## Control Flow

Postcore init registers the platform driver. Probe maps PMU MMIO, allocates global context, selects match data, creates either secure SMC-backed regmap or syscon regmap, initializes CPU PM state for GS101 if needed, calls optional PMU init, adds MFD cell `exynos-clkout`, and populates children. `exynos_sys_powerdown_conf()` later writes SoC powerdown tables for AFTR/LPA/SLEEP.

## State and Persistence Behavior

Global `pmu_base_addr` and `pmu_context` are singleton state. PMU register writes persist in hardware until reset or later writes. GS101 CPU PM flags persist in memory and are protected by `cpupm_lock`. Suspend/reboot notifiers gate cpuidle hint programming.

## Dependencies and Integration Points

It depends on platform MMIO, syscon/regmap, secure Tensor SMC regmap hooks, MFD, OF population, cpuhotplug, CPU PM notifiers, reboot notifiers, and SoC-specific `exynos_pmu_data`.

## Risks and Edge Cases

Singleton globals assume one PMU. CPU hotplug states and notifiers are registered without corresponding teardown in visible code, acceptable for non-removable PMU but risky for bind/unbind testing. `exynos_get_pmu_regmap_by_phandle()` calls `put_device(dev)` before returning `syscon_node_to_regmap(pmu_np)`, relying on syscon lifetime. GS101 raw spinlock paths must remain IRQ-safe and not call sleeping regmap implementations.

## Test Signals

Boot legacy Exynos and GS101, verify PMU regmap lookup by phandle, secure and syscon regmap paths, powerdown table writes for all modes, MFD child creation, CPU hotplug/cpuidle hint programming, suspend/reboot flag behavior, and no lockdep splats in CPU PM notifiers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/samsung/exynos-pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/samsung/exynos-pmu.h -->
# sources/distributed-fs/ceph-client/drivers/soc/samsung/exynos-pmu.h

## Purpose

`exynos-pmu.h` is the private PMU interface for generic and SoC-specific Exynos PMU code. It defines powerdown table records, match-data shape, exported data symbols, raw PMU helpers, and secure Tensor register callbacks.

## Important APIs, Types, and Functions

`PMU_TABLE_END` terminates `struct exynos_pmu_conf` arrays. `struct exynos_pmu_data` contains optional config tables, secure-regmap and CPU-PM flags, init and powerdown callbacks, and regmap access tables. Externs expose ARM PMU data sets and `gs101_pmu_data`. `pmu_raw_writel()`, `pmu_raw_readl()`, `tensor_sec_reg_write()`, `tensor_sec_reg_read()`, and `tensor_sec_update_bits()` are declared.

## Control Flow

Generic PMU probe receives an `exynos_pmu_data` pointer from OF match data and calls the callbacks or table fields at probe and suspend/powerdown time. SoC-specific files only export data conforming to this header.

## State and Persistence Behavior

The header declares structures; runtime state lives in `exynos-pmu.c` and hardware PMU registers.

## Dependencies and Integration Points

It depends on Exynos PMU register definitions for `NUM_SYS_POWERDOWN` and on regmap access tables. It links generic PMU code to SoC-specific table files and secure GS101 support.

## Risks and Edge Cases

Table arrays must terminate with `PMU_TABLE_END`; missing terminators cause out-of-bounds writes. Callback ordering in `exynos_sys_powerdown_conf()` depends on the distinction between primary and extra tables/callbacks. ARM-data externs are conditional on `CONFIG_EXYNOS_PMU_ARM_DRIVERS`.

## Test Signals

Compile with and without ARM PMU drivers, validate every table terminator, and exercise powerdown callbacks for all `enum sys_powerdown` modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/samsung/exynos-pmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/samsung/exynos-regulator-coupler.c -->
# sources/distributed-fs/ceph-client/drivers/soc/samsung/exynos-regulator-coupler.c

## Purpose

`exynos-regulator-coupler.c` registers an Exynos-specific regulator coupler for Exynos5800. It balances voltages across coupled regulators while preserving current voltage when consumers have not yet applied constraints.

## Important APIs, Types, and Functions

`regulator_get_optimal_voltage()` computes a safe target range for one regulator considering consumers, constraints, current voltages, and max-spread. `exynos_coupler_balance_voltage()` repeatedly picks the coupled regulator with the largest useful voltage delta and calls `regulator_set_voltage_rdev()`. `exynos_coupler_attach()` is a no-op. `exynos_coupler_init()` registers the coupler only on `samsung,exynos5800`.

## Control Flow

At arch init, machine compatibility is checked. During regulator coupling, the core calls `balance_voltage()`, which loops through coupled regulators under regulator locks, computes optimal voltages, applies the best next change, and repeats until no change is needed or an error occurs.

## State and Persistence Behavior

No private state is stored. Voltage changes mutate regulator hardware state through regulator core operations.

## Dependencies and Integration Points

It depends on OF machine matching and regulator coupler internals, including locked `regulator_dev` objects, consumer checks, and coupling constraints. It is tailored for Exynos5800 coupled rails.

## Risks and Edge Cases

The code uses regulator core internal-style helpers and assumes locks are held. The loop condition `while (n_coupled > 1)` relies on internal done-bit logic to exit through `!best_rdev`; regressions could spin if deltas never settle. Incorrect max-spread constraints can reject valid configurations or permit unsafe rail differences.

## Test Signals

Test on Exynos5800 with coupled CPU rails, including no consumer constraints, conflicting constraints, suspend-state balancing, voltage raise/lower paths, and max-spread violations. Use lockdep to verify regulator lock assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/samsung/exynos-regulator-coupler.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/samsung/exynos-usi.c -->
# sources/distributed-fs/ceph-client/drivers/soc/samsung/exynos-usi.c

## Purpose

`exynos-usi.c` configures Samsung Universal Serial Interface blocks to expose a selected UART, SPI, I2C, or combined protocol mode. It writes system-register SW_CONF fields, controls clocks, enables USIv2 blocks, and populates child protocol devices.

## Important APIs, Types, and Functions

`struct exynos_usi_variant` describes USI version, SW_CONF mask, valid mode range, and required clocks. `struct exynos_usi` stores MMIO, clocks, sysreg regmap, mode, and variant. `exynos_usi_set_sw_conf()` writes protocol mode. `exynos_usi_enable()` clears reset and configures clock request for USIv2. `exynos_usi_configure()/unconfigure()` handle version-specific setup. `exynos_usi_parse_dt()` reads `samsung,mode`, `samsung,sysreg`, and `samsung,clkreq-on`.

## Control Flow

Probe allocates state, selects variant data, parses DT, gets clocks, maps USIv2 MMIO, configures selected mode, installs a devm cleanup action, and populates child nodes. Resume noirq reconfigures the mode because hardware resets across suspend.

## State and Persistence Behavior

Driver state records current mode and resources. SW_CONF and USI registers persist until reset/suspend; resume re-applies them. Child devices exist under the USI node after OF population.

## Dependencies and Integration Points

It depends on syscon/regmap, clocks, platform MMIO, OF child population, PM callbacks, and `dt-bindings/soc/samsung,exynos-usi.h`. Protocol drivers bind to child nodes after USI configuration.

## Risks and Edge Cases

Invalid `samsung,mode` rejects probe. USIv1 keeps clocks enabled until cleanup, while USIv2 toggles around register programming. `of_platform_populate()` has no paired depopulate in the visible code because devm handles only USI unconfigure, not child depopulation. Resume failures may leave child protocol hardware unusable.

## Test Signals

Test each supported mode on Exynos850 and Exynos8895 variants, invalid modes, missing sysreg phandle, clock failures, suspend/resume restoration, `samsung,clkreq-on`, and child device probing order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/samsung/exynos-usi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/samsung/exynos3250-pmu.c -->
# sources/distributed-fs/ceph-client/drivers/soc/samsung/exynos3250-pmu.c

## Purpose

`exynos3250-pmu.c` supplies Exynos3250 PMU powerdown tables and initialization callbacks to the generic Exynos PMU driver.

## Important APIs, Types, and Functions

`exynos3250_pmu_config[]` lists PMU register values for AFTR, W-AFTR/LPA, and sleep modes, terminated by `PMU_TABLE_END`. `exynos3250_powerdown_conf_extra()` configures SC feedback/counters and sleep durations. `exynos3250_pmu_init()` sets ACE/ACP behavior, standby WFI, and PSHOLD output/enables. `exynos3250_pmu_data` exports the table and callbacks.

## Control Flow

Generic PMU probe calls `pmu_init()`. Later `exynos_sys_powerdown_conf()` writes the main table and invokes the extra callback for the selected powerdown mode.

## State and Persistence Behavior

No private state exists. Calls write PMU registers through `pmu_raw_readl/writel`; those settings persist in PMU hardware until reset or subsequent power-management writes.

## Dependencies and Integration Points

It depends on Exynos PMU register definitions and the generic PMU data contract in `exynos-pmu.h`. It is built only when ARM PMU driver data is enabled.

## Risks and Edge Cases

Table ordering and mode columns must match `enum sys_powerdown`. Missing terminator would overrun in generic code. PSHOLD and standby settings are board-critical and should not be changed casually.

## Test Signals

Boot Exynos3250, verify PMU init register effects, exercise AFTR/W-AFTR/SLEEP table writes, confirm durations in sleep mode, and validate suspend/resume and power-off behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/samsung/exynos3250-pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/samsung/exynos4-pmu.c -->
# sources/distributed-fs/ceph-client/drivers/soc/samsung/exynos4-pmu.c

## Purpose

`exynos4-pmu.c` provides PMU powerdown configuration tables for Exynos4210, Exynos4212, and Exynos4412 to the generic Exynos PMU driver.

## Important APIs, Types, and Functions

`exynos4210_pmu_config[]` covers Exynos4210 low-power registers. `exynos4x12_pmu_config[]` covers Exynos4212/4412 baseline registers. `exynos4412_pmu_config[]` adds core 2/3 entries for quad-core Exynos4412. Exported `exynos4210_pmu_data`, `exynos4212_pmu_data`, and `exynos4412_pmu_data` reference these tables.

## Control Flow

Generic PMU match data selects the relevant `exynos_pmu_data`. When entering a system powerdown mode, `exynos_sys_powerdown_conf()` iterates the primary table and then optional extra table for Exynos4412.

## State and Persistence Behavior

The file contains static configuration data only. Runtime state is PMU hardware register contents after generic table writes.

## Dependencies and Integration Points

It depends on Exynos PMU register definitions and generic PMU table iteration. It is ARM-only PMU data selected by Kconfig.

## Risks and Edge Cases

Mode-value columns must align with AFTR, LPA, and SLEEP. Exynos4412 requires both baseline and extra tables; missing the extra table would skip cores 2/3. Hardware register definitions must match the SoC revision.

## Test Signals

Suspend/resume tests on Exynos4210, 4212, and 4412; verify table terminators; inspect PMU writes for each powerdown mode; and validate quad-core CPU retention/powerdown behavior on 4412.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/samsung/exynos4-pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/samsung/exynos5250-pmu.c -->
# sources/distributed-fs/ceph-client/drivers/soc/samsung/exynos5250-pmu.c

## Purpose

`exynos5250-pmu.c` supplies Exynos5250 PMU low-power configuration and initialization callbacks. It prepares watchdog reset behavior and option-register settings for system powerdown modes.

## Important APIs, Types, and Functions

`exynos5250_pmu_config[]` lists AFTR/LPA/SLEEP register values. `exynos5_list_both_cnt_feed[]` names option registers that should use both SC feedback and counters. `exynos5_list_disable_wfi_wfe[]` names option registers whose standby WFI/WFE bits are cleared. `exynos5250_pmu_init()` unmasks watchdog reset requests. `exynos5_powerdown_conf()` applies option-register updates before table writes. `exynos5250_pmu_data` exports the config.

## Control Flow

Generic PMU probe invokes `pmu_init()`. On powerdown configuration, `exynos_sys_powerdown_conf()` first calls `powerdown_conf()`, then iterates the PMU table for the requested mode.

## State and Persistence Behavior

All state changes are PMU register writes. Static arrays are immutable. No driver-private state is stored.

## Dependencies and Integration Points

It depends on Exynos5 PMU register definitions and the generic PMU framework. It is compiled as ARM PMU data.

## Risks and Edge Cases

Watchdog reset unmasking is critical for system recovery. Option-register updates affect CPU and peripheral low-power entry; incorrect bits can break suspend/resume. Table termination and mode-column alignment are required for safe iteration.

## Test Signals

Validate watchdog reset behavior, AFTR/LPA/SLEEP entry and resume, option-register values after `powerdown_conf()`, and PMU table writes against hardware documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/samsung/exynos5250-pmu.c -->
