# subset-b-005957 Research

Grouped research for Tegra SoC integration headers and AC97 bus compatibility headers under `sources/distributed-fs/ceph-client/include`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/tegra/bpmp-abi.h -->
# sources/distributed-fs/ceph-client/include/soc/tegra/bpmp-abi.h

## Purpose

`bpmp-abi.h` is the wire-format contract for messages exchanged with NVIDIA Tegra BPMP firmware over IPC/IVC channels. It defines message request and response headers, legal MRQ numeric IDs, packed payload structures, sub-command enums, fixed buffer lengths, ABI compatibility constants, and BPMP-local error numbers. It is deliberately firmware-facing and platform-versioned: many message families are conditionally documented for T186, T194, T234/T238, TH500/TB500, and T264 variants.

## Important APIs, Types, and Constants

The top-level ABI types are `struct mrq_request` and `struct mrq_response`. `mrq_request.mrq` selects one MRQ service, while `flags` can carry `BPMP_MAIL_DO_ACK`, `BPMP_MAIL_RING_DB`, and `BPMP_MAIL_CRC_PRESENT`. With CRC enabled, the flags word is interpreted as options, transaction ID, payload length, and CRC16. The response header returns `err` plus matching CRC-related metadata. `MSG_MIN_SZ` and `MSG_DATA_MIN_SZ` define the minimum IPC frame and payload sizes used by client wrappers.

The file defines MRQ IDs from basic liveness (`MRQ_PING`, `MRQ_THREADED_PING`) through platform management (`MRQ_RESET`, `MRQ_CLK`, `MRQ_PG`, `MRQ_THERMAL`, `MRQ_SHUTDOWN`) and newer services such as `MRQ_BWMGR_INT`, `MRQ_C2C`, `MRQ_PCIE`, `MRQ_HWPM`, `MRQ_DVFS`, and `MRQ_PPP_PROFILE`. Each complex MRQ has a request struct containing a command selector and a packed anonymous union of command-specific payloads, plus a response struct or union for command-specific return data.

Key families include `mrq_clk_request/response` for rate, parent, enable, all-info, max-ID, and fmax-at-vmin queries; `mrq_pg_request/response` for BPMP power-domain state and names; thermal host-to-BPMP and BPMP-to-host request types for temperature, thermtrip, and trip notifications; debug and ring-buffer console payloads; memory bandwidth and latency payloads; UPHY, FMON, EC, telemetry, power-limit, power-model, power-controller, SLC, C2C, PCIe, CR7, HWPM, DVFS, and PPP profile payloads. Error constants such as `BPMP_EBADCMD`, `BPMP_EBADMSG`, `BPMP_ENOTSUP`, and `BPMP_ENAVAIL` are ABI error numbers that callers use negated in `mrq_response.err`.

## Control Flow and Protocol Behavior

This header has no executable implementation. Its control flow is encoded as an RPC protocol: a caller fills `mrq_request`, serializes the MRQ-specific payload immediately after it, sends the frame, and optionally waits for `mrq_response` plus response payload. `MRQ_QUERY_ABI` and many per-family `*_QUERY_ABI` subcommands are discovery gates that clients should use before relying on optional or platform-specific operations. Some services are bidirectional: for example, host thermal trip configuration can later cause BPMP to send an `MRQ_THERMAL` request back to the host.

Several command selectors pack state into bitfields. `mrq_clk_request.cmd_and_id` stores the clock command in bits 31..24 and clock ID in bits 23..0; `mrq_fmon_request.cmd_and_id` uses the same style for FMON command and monitored clock ID. I2C transactions serialize variable-length `serial_i2c_request` records inside a bounded byte buffer, requiring length-based walking instead of direct array indexing.

## State and Persistence

The ABI itself persists nothing, but many operations mutate persistent or long-lived firmware/hardware state. Clock rate, parent, and enable requests affect BPMP-owned clock state; reset and power-gate operations change hardware domain state; thermal trips, bandwidth manager requests, power limits, DVFS states, SLC bypass, power-controller bypass, C2C training, PCIe endpoint setup, and HWPM stream configuration can outlive the IPC transaction. Debug and console operations carry file handles, FIFO positions, or shared buffer addresses whose lifetime is owned by firmware.

## Dependencies and Integration Points

The header depends only on basic integer and size types when compiled outside the kernel and on packing/anonymous-union compatibility macros. Kernel client code such as `soc/tegra/bpmp.h` uses `MSG_DATA_MIN_SZ` and these payload definitions when marshalling mailbox or IVC frames. Other Tegra subsystems integrate through the MRQ families: clock drivers, reset controllers, generic power domains, thermal framework, memory controller/interconnect code, PCIe/UPHY drivers, debugfs mirror code, and platform monitoring code.

## Risks and Edge Cases

The dominant risk is ABI drift. All payloads are packed and many contain fixed-size arrays constrained by `MSG_DATA_MIN_SZ`; padding, alignment, endian assumptions, and compiler handling of anonymous unions are part of the contract. CRC-enabled communication adds strict payload length and CRC requirements, and functional-safety platform configurations may reject frames with `BPMP_EBADMSG` if metadata is absent or wrong. Variable-length payloads, especially I2C and debug writes, require explicit bounds checks. Platform-conditional support means clients must query support and handle `-BPMP_ENODEV`, `-BPMP_ENOTSUP`, and `-BPMP_EBADCMD` rather than assuming all documented commands are present. Several commands program hardware with caller-provided identifiers or class codes; invalid requests can return errors or, where the ABI documents no firmware validation, place responsibility on the requester.

## Test Signals

Useful tests are ABI-level compile and layout checks, including `sizeof`, offset, and packed-layout assertions via `BPMP_ABI_CHECKS`; MRQ marshalling tests that verify headers, command fields, payload lengths, CRC16 calculation, and transaction IDs; negative tests for unsupported MRQs/subcommands; and integration tests that query ABI support before performing clock, reset, thermal, powergate, bandwidth, and debug operations. On hardware or firmware simulators, ping/threaded ping, query tag, query ABI, and read-only info commands are low-risk smoke tests before state-changing MRQs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/tegra/bpmp-abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/tegra/bpmp.h -->
# sources/distributed-fs/ceph-client/include/soc/tegra/bpmp.h

## Purpose

`bpmp.h` is the kernel-facing interface for the Tegra BPMP client driver. It wraps the firmware ABI from `bpmp-abi.h` in Linux device, mailbox, IVC, reset, clock, power-domain, and debugfs abstractions. Consumers use this header to obtain a `struct tegra_bpmp`, send MRQ messages, register handlers for BPMP-initiated MRQs, and initialize optional BPMP-backed provider subsystems.

## Important APIs, Types, and Functions

`struct tegra_bpmp_soc` describes SoC-specific channel layout and reset count. `struct tegra_bpmp_mb_data` is the mailbox frame shape with `code`, `flags`, and `data[MSG_DATA_MIN_SZ]`; the `tegra_bpmp_mb_*` macros use `iosys_map` helpers to read/write fields and payload bytes. `struct tegra_bpmp_channel` binds a BPMP instance to input/output maps, a completion, optional `tegra_ivc`, and channel index. `struct tegra_bpmp` is the driver state: mailbox client/channel, atomic TX lock, TX/RX/threaded channels, threaded-channel allocation and busy bitmaps, MRQ handler list and lock, clock/reset/genpd/debugfs state, and suspend flag.

The public API includes `tegra_bpmp_get()`, `tegra_bpmp_get_with_id()`, `tegra_bpmp_put()`, `tegra_bpmp_transfer_atomic()`, `tegra_bpmp_transfer()`, `tegra_bpmp_mrq_return()`, `tegra_bpmp_request_mrq()`, `tegra_bpmp_free_mrq()`, and `tegra_bpmp_mrq_is_supported()`. Optional initializer hooks expose clocks, resets, powergates, and debugfs when their config symbols are enabled.

## Control Flow and State

Callers acquire a BPMP handle, prepare `struct tegra_bpmp_message` with MRQ ID, TX buffer, RX buffer, and flags such as `TEGRA_BPMP_MESSAGE_RESET`, then transfer it through the atomic or sleeping path. The implementation chooses a channel, writes mailbox/IVC payload bytes, waits for completion if needed, and copies response data back. BPMP-originated MRQs are dispatched through the registered `struct tegra_bpmp_mrq` list, and handlers reply with `tegra_bpmp_mrq_return()`.

State is held in the BPMP instance and includes channel allocation, outstanding threaded transactions, provider registrations, and the list of inbound MRQ callbacks. The header itself does not persist data, but the driver state mirrors firmware communication resources and must be synchronized with spinlocks and semaphores.

## Dependencies and Integration Points

The header depends on Linux `iosys-map`, mailbox, PM domain, reset-controller, semaphore, list, spinlock, and device infrastructure, plus `soc/tegra/bpmp-abi.h`. It integrates with Tegra clock, reset, generic power-domain, debugfs, and IVC code. Fallback stubs return `-ENODEV` or `false` when `CONFIG_TEGRA_BPMP` or provider-specific options are disabled, allowing consumers to compile without runtime BPMP support.

## Risks and Test Signals

Main risks are concurrency bugs around channel allocation and atomic transfers, incorrect payload sizing against `MSG_DATA_MIN_SZ`, lost completions, using sleeping transfers in atomic contexts, and stale MRQ handlers after device teardown. Tests should compile both enabled and disabled configs, exercise ping/query ABI transfers, verify atomic and threaded paths, validate MRQ handler registration/removal, and probe optional clock/reset/powergate/debugfs init paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/tegra/bpmp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/tegra/common.h -->
# sources/distributed-fs/ceph-client/include/soc/tegra/common.h

## Purpose

`common.h` provides small cross-driver helpers for Tegra SoC detection and core-device OPP table initialization. It lets generic Tegra device drivers ask whether they are running on Tegra and initialize an operating-points table without hard failing on non-Tegra or disabled Tegra builds.

## Important APIs, Types, and Functions

`struct tegra_core_opp_params` contains `init_state`, currently the only option for pre-initializing OPP state. With `CONFIG_ARCH_TEGRA`, the header declares `soc_is_tegra()` and `devm_tegra_core_dev_init_opp_table()`. Without that config, static inline stubs return `false` and `-ENODEV`. `devm_tegra_core_dev_init_opp_table_common()` is the convenience wrapper: it creates zeroed params, sets `init_state = true`, calls the main OPP initializer, and converts `-ENODEV` into success.

## Control Flow and State

The only executable logic is the common wrapper. It treats missing Tegra OPP support as a non-error so a shared driver can call it unconditionally. Any real OPP table state is owned by the implementation behind `devm_tegra_core_dev_init_opp_table()` and is device-managed by the Linux driver model.

## Dependencies and Integration Points

The file includes Linux errno and types and forward-declares `struct device`. It integrates with Tegra SoC code and the Linux OPP framework through the implementation file outside this header.

## Risks and Test Signals

The subtle risk is error normalization: `-ENODEV` is intentionally ignored by the wrapper, while all other errors propagate. Tests should cover enabled and disabled `CONFIG_ARCH_TEGRA` builds, OPP success, missing OPP support, and propagation of real failures such as malformed OPP tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/tegra/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/tegra/cpuidle.h -->
# sources/distributed-fs/ceph-client/include/soc/tegra/cpuidle.h

## Purpose

`cpuidle.h` exposes a single Tegra cpuidle coordination hook for PCIe IRQ usage. It gives other Tegra code a compile-time-safe way to notify the cpuidle subsystem that PCIe interrupts are in use.

## Important APIs, Types, and Functions

When `CONFIG_ARM_TEGRA_CPUIDLE` is enabled, the header declares `tegra_cpuidle_pcie_irqs_in_use()`. Otherwise it provides an empty inline stub. There are no data structures or constants.

## Control Flow and State

The header contains no local state. The enabled implementation likely updates cpuidle policy or wake/IRQ bookkeeping so low-power states do not break active PCIe interrupt handling. The disabled stub intentionally makes notification a no-op.

## Dependencies and Integration Points

It has no includes and only depends on the cpuidle config symbol. Integration is expected from Tegra PCIe or interrupt setup code that must inform cpuidle about wake or IRQ constraints.

## Risks and Test Signals

Risk is primarily configuration-dependent behavior: callers may assume the hook has an effect when it compiles to a no-op. Tests should include builds with and without `CONFIG_ARM_TEGRA_CPUIDLE` and platform suspend/resume or PCIe interrupt wake tests on enabled hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/tegra/cpuidle.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/tegra/flowctrl.h -->
# sources/distributed-fs/ceph-client/include/soc/tegra/flowctrl.h

## Purpose

`flowctrl.h` defines Tegra flow-controller register offsets, bit masks, and optional function prototypes for CPU halt, WFE/WFI, suspend entry, and suspend exit coordination. It is used by low-level power-management and CPU bring-up code.

## Important APIs, Types, and Functions

The constants describe flow-controller event registers and CPU CSR fields, including `FLOW_CTRL_HALT_CPU*_EVENTS`, `FLOW_CTRL_WAITEVENT`, `FLOW_CTRL_WAIT_FOR_INTERRUPT`, resume sources, IRQ/FIQ halt masks, `FLOW_CTRL_CPU*_CSR`, interrupt/event flags, external rail enable bits, and Tegra20/Tegra30 WFE/WFI bitmaps. Outside assembly, `CONFIG_SOC_TEGRA_FLOWCTRL` enables `flowctrl_read_cpu_csr()`, `flowctrl_write_cpu_csr()`, `flowctrl_write_cpu_halt()`, `flowctrl_cpu_suspend_enter()`, and `flowctrl_cpu_suspend_exit()`. Disabled builds return zero or do nothing.

## Control Flow and State

The functions are register access and suspend sequencing hooks. Callers write per-CPU halt mode and CSR values before entering low-power paths, then restore or clear state on exit. Register state persists in the flow-controller hardware, not in this header.

## Dependencies and Integration Points

The header avoids C declarations for assembly users. C users need `u32` from surrounding includes. It integrates with Tegra ARM power management, secondary CPU parking, cpuidle, and platform suspend code.

## Risks and Test Signals

Incorrect bit selection can leave CPUs halted, wake on the wrong source, or fail suspend/resume. Assembly inclusion also means changes must preserve preprocessor cleanliness. Test signals include SMP boot, CPU hotplug, LP2/suspend entry and exit, IRQ/FIQ wake behavior, and builds with flow-controller support disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/tegra/flowctrl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/tegra/fuse.h -->
# sources/distributed-fs/ceph-client/include/soc/tegra/fuse.h

## Purpose

`fuse.h` exposes Tegra chip, SKU, revision, platform, strap, RAM code, and fuse-reading interfaces. Drivers use it to identify SoC generation and process/SKU characteristics that influence clocks, OPPs, calibration, platform quirks, and safety behavior.

## Important APIs, Types, and Functions

The header defines chip ID constants such as `TEGRA20`, `TEGRA186`, `TEGRA234`, `TEGRA241`, and `TEGRA264`, plus notable fuse offsets including SKU and calibration registers. `enum tegra_revision` enumerates silicon revisions from unknown through A04. `enum tegra_platform` identifies silicon, FPGA, simulation, VDK, VSP, and related platforms. `struct tegra_sku_info` holds SKU ID, CPU/SoC/GPU process and speedo IDs/values, IDDQ values, revision, and platform.

With `CONFIG_ARCH_TEGRA`, the file exports global `tegra_sku_info` and functions including `tegra_read_straps()`, `tegra_read_ram_code()`, `tegra_fuse_readl()`, `tegra_read_chipid()`, `tegra_get_chip_id()`, `tegra_get_platform()`, `tegra_is_silicon()`, and `tegra194_miscreg_mask_serror()`. Disabled builds provide zero/false or `-ENODEV` stubs and a private unused `tegra_sku_info`. `tegra_soc_device_register()` is declared outside the config block for registering the SoC device.

## Control Flow and State

Runtime implementations read immutable fuse or strap registers and populate process-wide SoC identity state. The header itself does not persist data, but `tegra_sku_info` is a global cache of hardware-derived identity. Consumers typically read it during probe or OPP/clock setup.

## Dependencies and Integration Points

The header depends on Linux types and, for C users, a forward-declared `struct device` returned by `tegra_soc_device_register()`. It integrates with SoC registration, OPP selection, thermal/calibration code, memory and display calibration users, and platform-specific errata handling.

## Risks and Test Signals

Risks include treating disabled-build stubs as real hardware values, using raw chip IDs without revision/platform checks, and relying on global SKU state before initialization. Tests should validate fuse reads on supported SoCs, non-Tegra compile stubs, SKU table selection, SoC device registration, and platform/revision-dependent driver paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/tegra/fuse.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/tegra/irq.h -->
# sources/distributed-fs/ceph-client/include/soc/tegra/irq.h

## Purpose

`irq.h` exposes a Tegra ARM interrupt helper to report pending SGIs. It lets low-level ARM Tegra code check for software-generated interrupts without directly coupling all callers to the implementation.

## Important APIs, Types, and Functions

When both `CONFIG_ARM` and `CONFIG_ARCH_TEGRA` are set, the header declares `tegra_pending_sgi()`. In other builds it provides a static inline implementation returning `false`.

## Control Flow and State

The enabled implementation likely inspects interrupt-controller state to determine whether an SGI is pending. The header owns no state and the disabled path makes SGI pending checks harmless on unsupported builds.

## Dependencies and Integration Points

The file includes Linux types for `bool`. It integrates with ARM Tegra power-management, idle, or interrupt code that needs to avoid entering states while SGIs are pending.

## Risks and Test Signals

The main risk is power-management logic relying on a stubbed `false` result in unsupported configurations. Tests should cover ARM Tegra builds, non-ARM builds, idle entry while SGIs are pending, and interrupt wake paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/tegra/irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/tegra/ivc.h -->
# sources/distributed-fs/ceph-client/include/soc/tegra/ivc.h

## Purpose

`ivc.h` declares the Tegra Inter-VM Communication shared-memory queue API. It is the transport layer used by BPMP and other firmware or peer-device channels to exchange fixed-size frames through paired RX/TX queues with notification callbacks.

## Important APIs, Types, and Functions

`struct tegra_ivc` stores the peer device, RX and TX `iosys_map` windows with positions and DMA physical addresses, a notification callback and opaque data, and queue geometry (`num_frames`, `frame_size`). The public API has two-step read/write operations: `tegra_ivc_read_get_next_frame()` peeks the next received frame into an `iosys_map`, and `tegra_ivc_read_advance()` consumes it; `tegra_ivc_write_get_next_frame()` exposes the next transmit frame, and `tegra_ivc_write_advance()` publishes it. `tegra_ivc_notified()` processes remote notifications and reset handshakes. `tegra_ivc_reset()` initializes shared-memory state after channel reservation. `tegra_ivc_align()`, `tegra_ivc_total_queue_size()`, `tegra_ivc_init()`, and `tegra_ivc_cleanup()` handle sizing and lifetime.

## Control Flow and State

The IVC flow is reset, wait for notification readiness, obtain a frame map, read or write payload bytes, and advance the corresponding queue. The channel keeps local RX/TX positions, while shared queue headers and frame data live in DMA-coherent or otherwise mapped memory. Notifications are explicit through the configured callback.

## Dependencies and Integration Points

The header depends on Linux device, DMA mapping, iosys-map, and types. BPMP channels in `bpmp.h` can embed a `struct tegra_ivc`; other remote-processor or firmware transports can use the same queue abstraction.

## Risks and Test Signals

Risks include queue desynchronization after reset, incorrect frame-size alignment, stale iosys maps, missing notification processing, and concurrent producers/consumers advancing queues out of order. Tests should cover alignment and total-size calculations, reset handshakes, full/empty queues, read/write advance sequencing, and integration with BPMP mailbox/IVC notifications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/tegra/ivc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/tegra/mc.h -->
# sources/distributed-fs/ceph-client/include/soc/tegra/mc.h

## Purpose

`mc.h` defines the Tegra memory-controller and Tegra SMMU integration model. It describes memory clients, stream-ID/SWGROUP metadata, memory timings, reset and hotreset operations, interconnect-provider hooks, error-register layouts, SoC descriptors, and the runtime `struct tegra_mc` device state.

## Important APIs, Types, and Functions

`struct tegra_mc_timing` binds a memory clock rate to EMEM register data. `struct tegra_mc_client` identifies a memory client, BPMP ID, ICC type, name, SWGROUP or stream ID, FIFO size, and register fields for SMMU enable, latency allowance, and SID overrides. SMMU metadata is modeled by `struct tegra_smmu_swgroup`, `struct tegra_smmu_group_soc`, and `struct tegra_smmu_soc`. Optional SMMU probe/remove APIs are declared under `CONFIG_TEGRA_IOMMU_SMMU`.

Reset support uses `struct tegra_mc_reset` and `struct tegra_mc_reset_ops` with hooks for hotreset assert/deassert, DMA block/unblock, idling checks, and status. Interconnect support uses `TEGRA_MC_ICC_TAG_DEFAULT`, `TEGRA_MC_ICC_TAG_ISO`, `struct tegra_mc_icc_ops`, `tegra_mc_icc_xlate()`, and exported `tegra_mc_icc_ops`. SoC-level behavior is described by `struct tegra_mc_soc`, including clients, EMEM regs, address bits, carveouts, SMMU, interrupt masks, reset ops, ICC ops, SoC ops, and register layout. `struct tegra_mc` holds BPMP, device, SMMU, MMIO pointers, clock, timings, channels, BWMGR support, reset controller, ICC provider, spinlock, and debugfs state.

Public APIs include `tegra_mc_write_emem_configuration()`, `tegra_mc_get_emem_device_count()`, `devm_tegra_memory_controller_get()`, `tegra_mc_probe_device()`, and `tegra_mc_get_carveout_info()`, with disabled stubs returning `-ENODEV`.

## Control Flow and State

Drivers probe a memory controller with a SoC descriptor, map registers, optionally attach SMMU and interconnect providers, register reset controls, load timings, and handle memory-controller interrupts. Runtime flows include writing EMEM timing configuration for a selected rate, translating device nodes to ICC nodes, applying bandwidth aggregation, probing child devices for memory-client setup, reading carveout information, and sequencing hotresets while blocking DMA.

State persists in hardware registers, stream-ID overrides, latency allowance settings, reset state, ICC aggregate state, timing arrays, and debugfs entries. `struct tegra_mc.lock` protects shared controller state.

## Dependencies and Integration Points

The header integrates Linux clocks, reset controller, interrupt handling, debugfs, interconnect, Tegra ICC, BPMP, SMMU/IOMMU, device tree phandles, and physical memory carveout users. It is central for display, multimedia, GPU, camera, and other DMA clients that consume memory bandwidth or need stream-ID configuration.

## Risks and Test Signals

Risks include incorrect client IDs or stream IDs causing DMA isolation failures, bad latency allowance or bandwidth aggregation harming real-time clients, hotreset without DMA quiescence, wrong EMEM timing writes, and interrupt decoding mismatches across SoCs. Tests should exercise SMMU attach/remove, ICC bandwidth requests including ISO tags, reset/hotreset sequencing, carveout queries, memory-controller fault interrupts, suspend/resume, and disabled-config stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/tegra/mc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/tegra/pm.h -->
# sources/distributed-fs/ceph-client/include/soc/tegra/pm.h

## Purpose

`pm.h` declares Tegra low-level suspend modes and ARM power-management hooks. It centralizes names for LP2, LP1, LP0, and readiness states, and exposes CPU suspend, resume, LP2, secondary CPU parking, and suspend initialization routines when Tegra ARM sleep support is enabled.

## Important APIs, Types, and Functions

`enum tegra_suspend_mode` defines `TEGRA_SUSPEND_NONE`, `TEGRA_SUSPEND_LP2`, `TEGRA_SUSPEND_LP1`, `TEGRA_SUSPEND_LP0`, `TEGRA_MAX_SUSPEND_MODE`, and `TEGRA_SUSPEND_NOT_READY`. With `CONFIG_PM_SLEEP && CONFIG_ARM && CONFIG_ARCH_TEGRA`, the header declares `tegra_pm_validate_suspend_mode()`, low-level `tegra_resume()`, `tegra30_pm_secondary_cpu_suspend()`, `tegra_pm_clear_cpu_in_lp2()`, `tegra_pm_set_cpu_in_lp2()`, `tegra_pm_enter_lp2()`, `tegra_pm_park_secondary_cpu()`, and `tegra_pm_init_suspend()`. Disabled builds provide no-op or `-ENOTSUPP` stubs.

## Control Flow and State

Suspend code validates the requested mode, initializes suspend support, parks or suspends secondary CPUs, marks CPU LP2 state, enters LP2, and resumes through the low-level resume entry. State is primarily hardware and platform PM bookkeeping; the header does not define storage.

## Dependencies and Integration Points

It depends on Linux errno and integrates with Tegra PMC (`pmc.h` includes it), flow controller, CPU idle/hotplug, suspend/resume assembly, and platform PM code.

## Risks and Test Signals

Incorrect suspend-mode validation or CPU parking can hang resume or corrupt secondary CPU state. Tests should include compile coverage for enabled/disabled configs, LP2 entry/exit, secondary CPU suspend, system suspend/resume for LP0/LP1/LP2 where supported, and validation fallback on unsupported platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/tegra/pm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/tegra/pmc.h -->
# sources/distributed-fs/ceph-client/include/soc/tegra/pmc.h

## Purpose

`pmc.h` declares the Tegra Power Management Controller API. It exposes CPU power control, powergate domain IDs, I/O pad IDs, object-oriented PMC accessors, legacy global wrappers, suspend-mode programming, and core-domain synchronization state.

## Important APIs, Types, and Functions

The header defines powergate IDs from CPU and 3D through PCIe, display, XUSB, VIC, NVDEC, audio, DFD, and VE2, with `TEGRA_POWERGATE_MAX` and alias `TEGRA_POWERGATE_3D0`. `enum tegra_io_pad` enumerates many pad groups such as audio, camera, CSI, DSI, DP/HDMI, eMMC/SDMMC, PCIe, UFS, USB, UART, SPI, GPIO, and AO/HV pads.

Always-declared CPU helpers are `tegra_pmc_cpu_is_powered()`, `tegra_pmc_cpu_power_on()`, and `tegra_pmc_cpu_remove_clamping()`. With `CONFIG_SOC_TEGRA_PMC`, callers can use `devm_tegra_pmc_get()`, `tegra_pmc_powergate_power_on/off/remove_clamping()`, `tegra_pmc_powergate_sequence_power_up()`, `tegra_pmc_io_pad_power_enable/disable()`, legacy `tegra_powergate_*()` and `tegra_io_pad_*()` wrappers, `tegra_pmc_set_suspend_mode()`, `tegra_pmc_enter_suspend_mode()`, and `tegra_pmc_core_domain_state_synced()`. Disabled builds return `-ENOSYS`, no-op, or `false`. `tegra_pmc_get_suspend_mode()` is available when both PMC and PM sleep are enabled, otherwise it returns `TEGRA_SUSPEND_NONE`.

## Control Flow and State

Powergate flows typically assert reset/disable clock externally, request PMC power-on, remove clamping, and use `tegra_pmc_powergate_sequence_power_up()` for the common sequence that returns with the clock enabled. I/O pad flows enable or disable pad power/voltage domains. Suspend flows program and enter PMC-controlled low-power mode. State persists in PMC hardware registers and power-domain rails rather than the header.

## Dependencies and Integration Points

The header depends on Linux reboot declarations and `soc/tegra/pm.h`. It integrates with clock, reset-control, generic power domains, CPU hotplug, system suspend, pinctrl/pad power, PCIe/USB/display/media power sequencing, and legacy Tegra drivers.

## Risks and Test Signals

Power sequencing mistakes can leave domains clamped, clocks enabled at the wrong time, or I/O pads unpowered. Legacy wrappers increase the chance of mixing global and device-managed PMC access. Tests should cover powergate on/off and clamp removal, sequence power-up with reset and clock ordering, I/O pad enable/disable, CPU power-on, suspend-mode get/set/enter, disabled-config stubs, and resume after powering multimedia or PCIe domains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/tegra/pmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/tegra/tegra-cbb.h -->
# sources/distributed-fs/ceph-client/include/soc/tegra/tegra-cbb.h

## Purpose

`tegra-cbb.h` declares common support for Tegra CBB, the coherent bus/interconnect error reporting block. It defines a small error-description type, a registerable CBB instance, operation callbacks, IRQ lookup, debugfs formatting helpers, and wrappers to enable or clear CBB fault/error state.

## Important APIs, Types, and Functions

`struct tegra_cbb_error` maps an error code to source and description text. `struct tegra_cbb` stores the device, ops table, and list node used by the common CBB registry. `struct tegra_cbb_ops` contains optional implementation hooks for debugfs display, interrupt enable, error enable, fault enable, stall enable, error clear, and status read. Public functions include `tegra_cbb_get_irq()`, printf-style `tegra_cbb_print_err()`, `tegra_cbb_print_cache()`, `tegra_cbb_print_prot()`, `tegra_cbb_register()`, `tegra_cbb_fault_enable()`, `tegra_cbb_stall_enable()`, `tegra_cbb_error_clear()`, and `tegra_cbb_get_status()`.

## Control Flow and State

A SoC-specific CBB driver fills `struct tegra_cbb` and callback ops, obtains secure and non-secure IRQs from a platform device, registers with the common layer, enables interrupts/fault/error reporting, and uses print helpers to render decoded faults to debugfs or logs. State is in the registered list node, callback implementation, and CBB hardware registers.

## Dependencies and Integration Points

The header includes Linux list support and uses `struct platform_device`, `struct seq_file`, and `struct device` declarations from surrounding kernel headers. It integrates with platform IRQ resources, debugfs/seq_file output, and SoC-specific CBB error decoders.

## Risks and Test Signals

Risks include missing callbacks, IRQ resource mismatches, stale status after error clear, and incomplete fault decoding. Tests should register a CBB instance, validate IRQ lookup for secure/non-secure resources, exercise callback wrappers with NULL-safe behavior in implementation, trigger or simulate CBB faults, and verify debugfs output formatting for cache/protection fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/tegra/tegra-cbb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/ac97/codec.h -->
# sources/distributed-fs/ceph-client/include/sound/ac97/codec.h

## Purpose

`codec.h` defines the newer AC97 codec bus-facing device and driver abstractions. It lets AC97 codec drivers match on vendor IDs, register/unregister with the AC97 bus, access the underlying Linux device, and store driver data.

## Important APIs, Types, and Functions

`AC97_ID()` combines two 16-bit vendor ID words into a single 32-bit identifier. `AC97_DRIVER_ID()` creates an `struct ac97_id` table entry with ID, mask, and private data. `struct ac97_id` represents match criteria and driver data. `struct ac97_codec_device` embeds `struct device`, sensed `vendor_id`, codec number on the AC-link, BIT_CLK pointer, and owning `struct ac97_controller`. `struct ac97_codec_driver` embeds `struct device_driver` and supplies `probe`, `remove`, optional `shutdown`, and a terminated `id_table`.

Helper conversions include `to_ac97_device()`, `to_ac97_driver()`, and `ac97_codec_dev2dev()`. With `CONFIG_AC97_BUS_NEW`, `snd_ac97_codec_driver_register()` and `_unregister()` are external APIs; disabled builds register successfully as a no-op and unregister as a no-op. `ac97_get_drvdata()` and `ac97_set_drvdata()` delegate to core device driver data. `snd_ac97_codec_get_platdata()` retrieves codec platform data.

## Control Flow and State

AC97 bus code instantiates up to four codec devices per AC-link, reads vendor IDs, matches them against driver ID tables using masks, and calls driver probe/remove/shutdown callbacks. Driver-specific state is attached to the embedded device via drvdata. Clock and controller ownership remain in `ac97_codec_device`.

## Dependencies and Integration Points

The header depends on Linux device infrastructure and forward declares `struct ac97_controller` and `struct clk`. It integrates with the AC97 controller bus, ALSA codec drivers, platform data, and the Linux driver core.

## Risks and Test Signals

Risks include incorrect vendor ID mask construction, no-op registration hiding missing `CONFIG_AC97_BUS_NEW`, lifetime issues around embedded `struct device`, and drvdata misuse after remove. Tests should cover ID/mask matching, driver registration and unregistration in enabled configs, disabled-config compilation, probe/remove callback ordering, platform data retrieval, and multiple codec numbers on one AC-link.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/ac97/codec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/ac97/compat.h -->
# sources/distributed-fs/ceph-client/include/sound/ac97/compat.h

## Purpose

`compat.h` provides a bridge from the newer `struct ac97_codec_device` bus model to the legacy ALSA `struct snd_ac97` representation. It exists for backward compatibility with older AC97 bus users and build operations.

## Important APIs, Types, and Functions

The header includes `<sound/ac97_codec.h>` to expose the legacy `struct snd_ac97` declaration and declares `snd_ac97_compat_alloc(struct ac97_codec_device *adev)` and `snd_ac97_compat_release(struct snd_ac97 *ac97)`. Allocation creates a legacy compatibility object for a new bus codec device, and release tears it down.

## Control Flow and State

Users allocate a compatibility object after or during codec-device setup, pass it to legacy AC97 paths that expect `struct snd_ac97`, and release it when the codec is removed. Persistent state lives in the allocated compatibility object and whatever legacy ALSA code attaches to it.

## Dependencies and Integration Points

The file depends on the legacy ALSA AC97 codec header and the new `struct ac97_codec_device` type from the AC97 bus model. It integrates old AC97 codec/controller code with the newer bus-device representation.

## Risks and Test Signals

Risks include lifetime mismatches between the compatibility object and the underlying codec device, double release, and incomplete initialization of fields expected by legacy code. Tests should allocate/release around codec probe/remove, exercise representative legacy users, run leak/double-free checks, and compile both old and new AC97 configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/ac97/compat.h -->
