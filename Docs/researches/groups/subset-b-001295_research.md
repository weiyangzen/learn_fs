# subset-b-001295 research

This grouped report covers the requested FPGA manager/bridge KUnit tests, Xilinx and TS-73xx FPGA manager/bridge drivers, and the FSI core/master/SBEFIFO/OCC drivers. Each source file has a delimited section for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/tests/fpga-bridge-test.c -->
# sources/distributed-fs/ceph-client/drivers/fpga/tests/fpga-bridge-test.c

## Purpose
`fpga-bridge-test.c` is a KUnit suite for the FPGA bridge core. It creates fake bridge devices, tracks bridge enable state through a minimal `fpga_bridge_ops`, and validates acquisition, exclusive get semantics, direct enable/disable, and list-oriented bridge helper behavior.

## Important APIs, types, and functions
The local fixtures are `struct bridge_stats` and `struct bridge_ctx`. `register_test_bridge()` allocates a KUnit device and registers a fake `struct fpga_bridge` using `fpga_bridge_register()`. `op_enable_set()` backs `fake_bridge_ops` and records the last requested enable state. Test cases cover `fpga_bridge_get()`, `fpga_bridge_put()`, `fpga_bridge_disable()`, `fpga_bridge_enable()`, `fpga_bridge_get_to_list()`, `fpga_bridges_disable()`, `fpga_bridges_enable()`, and `fpga_bridges_put()`.

## Control flow
Suite initialization registers one fake bridge and stores it in `test->priv`. The get test retrieves that bridge by parent device, verifies the second get is rejected with `-EBUSY`, then releases it. The toggle test drives disable and enable calls and checks the private state flag. The list test registers a second fake bridge, pushes both bridges into a list, disables and enables the whole list, then releases all list entries and checks the list is empty.

## State and persistence behavior
State is entirely test-local. KUnit owns allocated contexts and test devices, while `kunit_add_action_or_reset()` guarantees bridge unregister on teardown. The only observed state is `bridge_stats.enable`; there is no persistence outside the test process.

## Dependencies and integration points
The file depends on KUnit device helpers and the public FPGA bridge API. It integrates with the bridge core through the real registration, reference, list, and operation dispatch paths rather than mocking the core internals.

## Risks and edge cases
The suite validates busy reference behavior and list cleanup, but it does not cover bridge operation failures, `enable_show`, multiple competing consumers beyond a duplicate get, or ordering semantics if bridge-list enable fails midway. Because the fake op always succeeds, rollback/error propagation is outside this test's signal.

## Test signals
Useful signals are KUnit pass/fail results for suite `fpga_bridge`, especially `-EBUSY` on a second get, correct `enable` transitions, and an empty bridge list after `fpga_bridges_put()`. Failures indicate regressions in bridge registration lifetime, exclusive access, list insertion order, or operation dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/tests/fpga-bridge-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/tests/fpga-mgr-test.c -->
# sources/distributed-fs/ceph-client/drivers/fpga/tests/fpga-mgr-test.c

## Purpose
`fpga-mgr-test.c` is a KUnit suite for the FPGA manager core programming sequence. It uses a fake manager that records operation order, manager state at each callback, and whether header/image payloads are passed to write callbacks as expected for both linear buffers and scatter-gather tables.

## Important APIs, types, and functions
The test fixture uses `struct mgr_stats` to record callback sequence numbers and states, and `struct mgr_ctx` to hold `fpga_image_info`, `fpga_manager`, and the backing KUnit device. Fake ops are `op_parse_header()`, `op_write_init()`, `op_write()`, `op_write_sg()`, and `op_write_complete()` in `fake_mgr_ops`, with `.skip_header = true`. Tests exercise `fpga_mgr_get()`, `fpga_mgr_put()`, `fpga_mgr_lock()`, `fpga_mgr_unlock()`, `fpga_mgr_load()`, `fpga_image_info_alloc()`, and `devm_fpga_mgr_register()`.

## Control flow
Initialization allocates image info, registers a fake manager, and arranges KUnit cleanup. `init_test_buffer()` creates a synthetic image with a fixed header region and payload region. The buffer load test sets `img_info->buf/count`, calls `fpga_mgr_load()`, then validates callback order: parse header, write init, write, write complete. The SG test builds a scatterlist-backed image and validates that `write_sg` sees the complete image but skips the header internally when checking payload bytes. The lock test checks a second lock returns `-EBUSY`.

## State and persistence behavior
All state lives in KUnit allocations and `mgr_stats`. The manager core state machine is sampled at each callback but not persisted. Scatter-gather resources and image info are released through KUnit actions.

## Dependencies and integration points
The suite depends on KUnit, the FPGA manager core, scatterlist helpers, and module/KUnit test registration. It integrates through the real `fpga_mgr_load()` path and therefore observes manager state transitions, header parsing, data-size/header-size updates, lock exclusion, and callback dispatch behavior.

## Risks and edge cases
The fake callbacks always return success, so failure unwinding, partial writes, timeout handling, firmware request loading, and manager unregister races are not covered. The SG validation assumes header skipping is correctly represented by `HEADER_SIZE`; malformed headers and zero-length payloads are not tested.

## Test signals
Suite `fpga_mgr` should pass with header and payload match flags set, monotonically increasing callback sequence numbers, expected manager states captured at each callback, `-EBUSY` on recursive lock, and successful buffer and SG loads. Regressions point to manager sequencing, header skip handling, or lock/reference behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/tests/fpga-mgr-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/tests/fpga-region-test.c -->
# sources/distributed-fs/ceph-client/drivers/fpga/tests/fpga-region-test.c

## Purpose
`fpga-region-test.c` is a KUnit suite for the FPGA region core. It verifies that a region can be found through class matching and that `fpga_region_program_fpga()` coordinates bridge acquisition/control with FPGA manager programming.

## Important APIs, types, and functions
The fixture combines fake manager, bridge, and region objects in `struct test_ctx`. `op_write()` increments manager programming count, `op_enable_set()` records bridge state and activation cycles, `fake_region_get_bridges()` populates `region->bridge_list`, and `fake_region_match()` supports class lookup. The tests cover `fpga_region_class_find()`, `fpga_region_register_full()`, `fpga_region_program_fpga()`, `devm_fpga_mgr_register()`, `fpga_bridge_register()`, and `fpga_bridges_put()`.

## Control flow
Suite init creates KUnit devices, registers a fake manager, a fake bridge, and a region whose `get_bridges` callback returns that bridge. The class-find test searches for a region with a parent-device predicate and releases the returned device reference. The programming test allocates an image, attaches it to the region, programs the FPGA, checks manager write count and bridge enable cycle count, releases the bridge list, and repeats the programming path to ensure the region can be reused.

## State and persistence behavior
State is test-local: `mgr_stats.write_count`, `bridge_stats.enable`, and `bridge_stats.cycles_count`. KUnit cleanup actions unregister image info, bridge, and region. No durable state is produced.

## Dependencies and integration points
The file depends on KUnit, FPGA manager, FPGA bridge, and FPGA region APIs. It integrates with the real region registration, class find, bridge list, and programming orchestration paths while using fake operations for the hardware-specific endpoints.

## Risks and edge cases
The test intentionally uses one bridge and a write-only fake manager, so it does not validate multiple-bridge rollback, bridge acquisition failure, manager load failures, overlay/DT-driven region behavior, or partial reconfiguration flags. Manual `fpga_bridges_put()` calls are needed after each program cycle because the region keeps the list populated.

## Test signals
Suite `fpga_region` should show successful class lookup, one manager write and one bridge activation per program call, and correct reuse after bridge-list release. Failures indicate regressions in region lookup, bridge orchestration, or manager handoff.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/tests/fpga-region-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/ts73xx-fpga.c -->
# sources/distributed-fs/ceph-client/drivers/fpga/ts73xx-fpga.c

## Purpose
`ts73xx-fpga.c` is an FPGA manager driver for the Altera Cyclone II FPGA on Technologic Systems TS-73xx boards. It bit-pushes configuration bytes through two MMIO registers and exposes the sequence through the Linux FPGA manager framework.

## Important APIs, types, and functions
`struct ts73xx_fpga_priv` stores the mapped register base and device pointer. Manager callbacks are `ts73xx_fpga_write_init()`, `ts73xx_fpga_write()`, and `ts73xx_fpga_write_complete()` in `ts73xx_fpga_ops`. Probe uses `devm_platform_ioremap_resource()` and `devm_fpga_mgr_register()`. Register bits include `TS73XX_FPGA_RESET`, `TS73XX_FPGA_WRITE_DONE`, `TS73XX_FPGA_CONFIG_LOAD`, and `TS73XX_FPGA_LOAD_OK`.

## Control flow
Probe maps the platform MMIO resource and registers an FPGA manager named `TS-73xx FPGA Manager`. Programming starts by dropping and reasserting reset with documented microsecond delays. The write callback polls the config register until the hardware is ready for each byte, then writes one byte to the data register. Completion toggles `CONFIG_LOAD`, waits, reads the status register, and returns `-ETIMEDOUT` if the load-ok bit is not set.

## State and persistence behavior
The driver keeps only the MMIO mapping and device pointer in managed memory. Programming state lives in board registers and the FPGA manager state machine; there is no persistent software state across unload or reboot.

## Dependencies and integration points
It depends on platform devices, MMIO helpers, `readb_poll_timeout()`, delay helpers, and the FPGA manager API. It integrates as a platform driver named `ts73xx-fpga-mgr`; board files or device tree/platform setup must provide the register resource.

## Risks and edge cases
The byte-at-a-time write path is sensitive to polling timeout, hardware-ready polarity, and register spacing. There is no explicit `.state` callback, partial-reconfiguration handling, firmware validation, or recovery beyond returning errors. Completion checks only `LOAD_OK`, so intermediate protocol failures may surface as timeout.

## Test signals
Build coverage, platform probe with a valid resource, successful manager registration, programming a known-good bitstream, timeout injection on `WRITE_DONE`, and `LOAD_OK` failure handling are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/ts73xx-fpga.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/versal-fpga.c -->
# sources/distributed-fs/ceph-client/drivers/fpga/versal-fpga.c

## Purpose
`versal-fpga.c` is the FPGA manager driver for Xilinx Versal devices. It delegates bitstream loading to the Xilinx firmware interface after setting the correct DMA addressing capability.

## Important APIs, types, and functions
The manager callbacks are `versal_fpga_ops_write_init()` and `versal_fpga_ops_write()` in `versal_fpga_ops`. Probe uses `dma_set_mask_and_coherent(..., DMA_BIT_MASK(44))` and `devm_fpga_mgr_register()`. The write path calls the Xilinx firmware FPGA load API with flags derived from `fpga_image_info`.

## Control flow
During probe, the platform device must support a 44-bit coherent DMA mask; otherwise the driver aborts. The write-init callback validates or records image flags without maintaining private state. The write callback passes the provided buffer and any partial-reconfiguration indication to platform firmware, which performs the actual programming operation.

## State and persistence behavior
This driver has essentially no private runtime state; registration is devm-managed and programming state is held by firmware and the FPGA manager core. There is no persistent state in the driver.

## Dependencies and integration points
It depends on the platform bus, OF match `xlnx,versal-fpga`, DMA mask setup, the FPGA manager framework, and Xilinx firmware services. It integrates with secure/platform firmware rather than programming PCAP registers directly.

## Risks and edge cases
The main risks are firmware-call failures, unsupported DMA masks, incorrect flag translation for partial reconfiguration, and lack of a state/status callback. Since the driver does not copy or DMA-map the buffer itself, buffer lifetime and firmware API expectations are critical integration assumptions.

## Test signals
Probe should fail cleanly without a 44-bit DMA-capable setup and register an FPGA manager when firmware is available. Programming tests should cover full and partial bitstreams, firmware failure returns, and device-tree matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/versal-fpga.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/xilinx-core.c -->
# sources/distributed-fs/ceph-client/drivers/fpga/xilinx-core.c

## Purpose
`xilinx-core.c` provides shared FPGA manager logic for Xilinx Spartan-6 and 7 Series slave-serial/selectmap-style configuration drivers. Transport drivers supply a byte-write callback while this core handles PROGRAM_B, INIT_B, DONE GPIO sequencing, manager state, full-bitstream validation policy, and post-write completion polling.

## Important APIs, types, and functions
The exported integration point is `xilinx_core_probe()`. Internal manager callbacks are `xilinx_core_state()`, `xilinx_core_write_init()`, `xilinx_core_write()`, and `xilinx_core_write_complete()`. `wait_for_init_b()` handles INIT_B polling or fallback delays, `get_done_gpio()` reads DONE, and `xilinx_core_devm_gpiod_get()` supports modern and legacy GPIO names for old slave-serial bindings.

## Control flow
Transport probes fill `struct xilinx_fpga_core` with `dev` and `write`, then call `xilinx_core_probe()`. Probe acquires PROGRAM_B, optional INIT_B legacy-compatible names, DONE, and registers an FPGA manager. Programming rejects `FPGA_MGR_PARTIAL_RECONFIG`, asserts PROGRAM_B low through the active-low GPIO abstraction, waits for INIT_B assert/deassert, verifies DONE is low, then waits program latency. The write callback delegates all bytes to the transport. Completion repeatedly writes `0xff` padding to supply extra CCLK cycles while polling DONE until `config_complete_timeout_us` expires, then reports INIT_B-derived diagnostic messages on timeout.

## State and persistence behavior
The core stores GPIO descriptors in the transport-owned `struct xilinx_fpga_core`. No file or firmware state is persisted. Hardware state is represented only through GPIO levels and the FPGA manager state callback, which reports reset when DONE is low and unknown otherwise.

## Dependencies and integration points
It depends on GPIO descriptors, OF compatibility checks for legacy names, delay/jiffies helpers, and the FPGA manager framework. It integrates with `xilinx-spi.c` and `xilinx-selectmap.c` through the `write` transport callback and exports `xilinx_core_probe()` as GPL.

## Risks and edge cases
Partial reconfiguration is explicitly unsupported. INIT_B may be absent, causing fixed fallback delays instead of positive hardware confirmation. Completion relies on the transport accepting one-byte padding writes, and diagnostics differ depending on INIT_B availability. GPIO polarity must be described correctly in firmware tables or reset sequencing will invert.

## Test signals
Signals include successful probe by both SPI and SelectMAP transports, rejection of partial reconfiguration, INIT_B timeout handling, DONE polling success after padding clocks, transport write failure propagation, and legacy `prog_b`/`init-b` GPIO-name compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/xilinx-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/xilinx-core.h -->
# sources/distributed-fs/ceph-client/drivers/fpga/xilinx-core.h

## Purpose
`xilinx-core.h` is the private shared interface between Xilinx transport-specific FPGA manager drivers and the common Xilinx configuration core.

## Important APIs, types, and functions
It defines `struct xilinx_fpga_core`, whose public fields are `struct device *dev` and `int (*write)(...)`. Private fields `prog_b`, `init_b`, and `done` are populated by `xilinx-core.c`. The sole function prototype is `xilinx_core_probe()`.

## Control flow
Transport drivers allocate or embed `struct xilinx_fpga_core`, initialize `dev` and `write`, then call `xilinx_core_probe()`. After that, FPGA manager callbacks in the core use the transport `write` operation for data and padding clocks.

## State and persistence behavior
The structure carries runtime-only pointers and GPIO descriptors. The header defines no persistent format and no executable logic.

## Dependencies and integration points
It depends on `linux/device.h`; the GPIO type is forward-used via pointers populated in the C file. It integrates `xilinx-spi.c`, `xilinx-selectmap.c`, and `xilinx-core.c`.

## Risks and edge cases
The comment separates public and private fields, but C cannot enforce that boundary. Transport drivers must keep the structure alive for the manager lifetime and must provide a valid `write` callback before probe.

## Test signals
Build coverage of both transports, successful manager probe, and write callback invocation through firmware loads validate the header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/xilinx-core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/xilinx-pr-decoupler.c -->
# sources/distributed-fs/ceph-client/drivers/fpga/xilinx-pr-decoupler.c

## Purpose
`xilinx-pr-decoupler.c` is an FPGA bridge driver for Xilinx PR Decoupler and DFX AXI Shutdown Manager IP. It exposes coupling/decoupling of a reconfigurable region through the FPGA bridge framework.

## Important APIs, types, and functions
`struct xlnx_pr_decoupler_data` stores match-specific naming, MMIO base, and AXI clock. Bridge ops are `xlnx_pr_decoupler_enable_set()` and `xlnx_pr_decoupler_enable_show()`. Probe uses `device_get_match_data()`, `devm_platform_ioremap_resource()`, `devm_clk_get("aclk")`, and `fpga_bridge_register()`.

## Control flow
Probe maps the control register, obtains and prepares the AXI clock, verifies it can be enabled, disables it, then registers an FPGA bridge with the matched IP name. `enable_set(true)` enables the clock, writes zero to couple traffic, disables the clock, and returns. `enable_set(false)` writes bit 0 to decouple/shutdown. `enable_show()` reads the same register and returns logical enabled when the register is zero. Remove unregisters the bridge and unprepares the clock.

## State and persistence behavior
The driver stores only MMIO, clock, and IP config pointers. Bridge state is the hardware control register; no software persistence exists.

## Dependencies and integration points
It depends on platform devices, OF match data for `xlnx,pr-decoupler*` and `xlnx,dfx-axi-shutdown-manager*`, clock APIs, MMIO helpers, and the FPGA bridge framework. FPGA regions can use this bridge to isolate logic during partial reconfiguration.

## Risks and edge cases
Clock enable failures block both set and show operations. The driver assumes register value zero means coupled and any nonzero value means decoupled. It does not use runtime PM, does not serialize bridge ops beyond bridge core locking, and does not validate clock/reset state after register writes.

## Test signals
Probe/remove with each compatible string, bridge enable/disable operations, `enable_show()` matching register state, clock failure injection, and region programming flows that include this bridge are useful validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/xilinx-pr-decoupler.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/xilinx-selectmap.c -->
# sources/distributed-fs/ceph-client/drivers/fpga/xilinx-selectmap.c

## Purpose
`xilinx-selectmap.c` is a transport driver that loads Xilinx Spartan-7, Artix-7, Kintex-7, and Virtex-7 bitstreams through the SelectMAP parallel configuration interface while reusing the common Xilinx FPGA manager core.

## Important APIs, types, and functions
`struct xilinx_selectmap_conf` embeds `struct xilinx_fpga_core` and stores the mapped data register. `xilinx_selectmap_write()` writes each byte to the mapped base address. `xilinx_selectmap_probe()` maps the resource, optionally configures active-low CSI_B and RDWR_B GPIOs, and calls `xilinx_core_probe()`.

## Control flow
Probe allocates the transport config, assigns the common core device and write callback, maps the SelectMAP MMIO resource, requests optional `csi` and `rdwr` GPIOs as inactive-high outputs, then delegates GPIO PROGRAM_B/INIT_B/DONE acquisition and manager registration to `xilinx_core_probe()`. During programming, the common core calls `xilinx_selectmap_write()` for data and completion padding; the transport loops byte-by-byte through MMIO writes.

## State and persistence behavior
Runtime state consists of the embedded core and MMIO base pointer. GPIOs and memory mappings are devm-managed. No persistent state exists.

## Dependencies and integration points
It depends on platform devices, OF compatible strings for 7-series SelectMAP variants, GPIO descriptors, MMIO helpers, and `xilinx-core`. It integrates as a transport layer beneath the FPGA manager core.

## Risks and edge cases
The byte-write loop has no hardware-ready polling, so board timing must be satisfied by the bus and common core sequence. Optional CSI/RDWR GPIOs are configured but not stored or toggled after probe. Incorrect resource width or GPIO polarity can silently break programming.

## Test signals
Build/probe for each compatible, successful firmware load through the manager, byte-write instrumentation on the MMIO aperture, optional GPIO absence/presence handling, and failure propagation from `xilinx_core_probe()` are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/xilinx-selectmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/xilinx-spi.c -->
# sources/distributed-fs/ceph-client/drivers/fpga/xilinx-spi.c

## Purpose
`xilinx-spi.c` is a slave-serial SPI transport for Xilinx Spartan-6 and 7 Series FPGA configuration. It supplies chunked SPI writes to the shared Xilinx FPGA manager core.

## Important APIs, types, and functions
`xilinx_spi_write()` implements the `xilinx_fpga_core.write` callback and sends firmware data with `spi_write()` in chunks of at most `SZ_4K`. `xilinx_spi_probe()` allocates `struct xilinx_fpga_core`, stores the SPI device as `core->dev`, and calls `xilinx_core_probe()`.

## Control flow
When the SPI driver probes a matching device, it registers through the common Xilinx core. During programming, the core handles GPIO sequencing and calls `xilinx_spi_write()`, which advances through the firmware buffer in 4 KiB strides and aborts on the first SPI transfer error.

## State and persistence behavior
The only private state is the devm-allocated `struct xilinx_fpga_core`. SPI controller/device state and FPGA programming state are external; no persistent state is stored.

## Dependencies and integration points
It depends on SPI core, OF/SPI IDs (`fpga-slave-serial`, `xlnx,fpga-slave-serial`), module SPI driver registration, and `xilinx-core`. The common core handles manager registration and GPIOs.

## Risks and edge cases
Large firmware images are serialized synchronously and depend on SPI controller behavior for chip select and clocking. Errors after partial writes cannot be recovered locally. The driver delegates partial-reconfiguration rejection and completion polling to `xilinx-core`.

## Test signals
SPI probe, successful manager registration, firmware writes larger and smaller than 4 KiB, SPI error propagation, and common-core completion behavior validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/xilinx-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/zynq-fpga.c -->
# sources/distributed-fs/ceph-client/drivers/fpga/zynq-fpga.c

## Purpose
`zynq-fpga.c` is the FPGA manager driver for Xilinx Zynq-7000 PCAP/devcfg. It programs the programmable logic via DMA to PCAP, manages SLCR reset/level-shifter sequencing, handles encrypted and partial bitstream flags, and uses interrupts/completions to feed the PCAP DMA queue.

## Important APIs, types, and functions
`struct zynq_fpga_priv` stores IRQ, clock, devcfg MMIO base, SLCR regmap, DMA queue state, spinlock, current SG pointer, and completion. Manager callbacks are `zynq_fpga_ops_write_init()`, `zynq_fpga_ops_write()` as `.write_sg`, `zynq_fpga_ops_write_complete()`, and `zynq_fpga_ops_state()`. Key helpers include `zynq_step_dma()`, `zynq_fpga_isr()`, `zynq_fpga_has_sync()`, `zynq_fpga_set_irq()`, and MMIO read/write wrappers.

## Control flow
Probe maps devcfg registers, resolves the `syscon` SLCR regmap, gets IRQ and `ref_clk`, unlocks devcfg, clears/masks interrupts, requests the IRQ, and registers the FPGA manager. Write-init enables the clock, validates encrypted bitstreams against secure-boot state, validates full bitstreams for the byte-swapped Xilinx sync word, asserts PL resets and level shifters for full reconfiguration, toggles `PCFG_PROG_B`, enables PCAP/PR control, checks the DMA queue is empty, and disables PCAP loopback. The write path validates SG alignment, DMA maps the table, enables the clock, clears interrupts, seeds DMA state under `dma_lock`, calls `zynq_step_dma()`, waits up to five seconds for completion, disables IRQs, checks error and done bits, unmaps DMA, and reports detailed register state on failure. Completion polls for `IXR_PCFG_DONE_MASK`, releases PR control back to ICAP, and restores level shifters/resets for full reconfiguration.

## State and persistence behavior
Runtime state is in `zynq_fpga_priv`, hardware registers, the DMA-mapped scatterlist, and one completion object. `dma_lock`, `dma_elm`, `dma_nelms`, and `cur_sg` coordinate the handoff between process context and interrupt context. No state persists across unload; reset and level-shifter changes are hardware-visible side effects.

## Dependencies and integration points
The driver depends on platform/OF resources, clocks, IRQs, DMA mapping, scatterlists, completions, spinlocks, MMIO polling, SLCR syscon regmap, PM headers, and FPGA manager APIs. It integrates with the generic FPGA manager by accepting SG images and exposing manager state from PCAP done status.

## Risks and edge cases
Critical risks are DMA queue race handling, inability to cancel a failed DMA, SG alignment restrictions, timeout/error bit interpretation, encrypted-bitstream secure-mode enforcement, and full-vs-partial reset/level-shifter behavior. The expression checking DMA queue empty is precedence-sensitive but intended to require queue-not-full and queue-empty. Hardware errata around PCAP loopback, level shifters, and sync-word byte order are central to correct operation.

## Test signals
Signals include probe with valid devcfg/syscon/IRQ/clock, full bitstream sync-word rejection, encrypted bitstream rejection when not secure, SG alignment failures, DMA completion interrupt path, timeout/error register diagnostics, partial reconfiguration without global PL reset, and final `FPGA_MGR_STATE_OPERATING` when PCFG_DONE is set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/zynq-fpga.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/zynqmp-fpga.c -->
# sources/distributed-fs/ceph-client/drivers/fpga/zynqmp-fpga.c

## Purpose
`zynqmp-fpga.c` is the FPGA manager driver for Xilinx ZynqMP PCAP. It copies bitstreams into coherent DMA memory and asks ZynqMP platform firmware to load them, exposing a sysfs status attribute for firmware configuration status.

## Important APIs, types, and functions
`struct zynqmp_fpga_priv` stores the device pointer and current FPGA manager flags. Manager callbacks are `zynqmp_fpga_ops_write_init()`, `zynqmp_fpga_ops_write()`, and `zynqmp_fpga_ops_state()`. `status_show()` exports `zynqmp_pm_fpga_get_config_status()`. Firmware calls include `zynqmp_pm_fpga_load()` and `zynqmp_pm_fpga_get_status()`.

## Control flow
Probe allocates private data and registers an FPGA manager named `Xilinx ZynqMP FPGA Manager`, with device attribute group `status`. Write-init records image flags. Write allocates a coherent DMA buffer, copies the bitstream, issues a write memory barrier, sets the partial flag if requested, calls firmware to load the FPGA, then frees the buffer. State reads firmware status and reports operating when `IXR_FPGA_DONE_MASK` is set.

## State and persistence behavior
The private `flags` field persists only between write-init and write for one load operation. Coherent DMA memory is allocated per write and freed immediately after the firmware call. Long-lived state is in platform firmware and FPGA hardware, not in the driver.

## Dependencies and integration points
It depends on coherent DMA APIs, FPGA manager, platform/OF matching `xlnx,zynqmp-pcap-fpga`, and the Xilinx ZynqMP firmware interface. The sysfs `status` file integrates firmware configuration status into the manager device.

## Risks and edge cases
Large bitstreams require a contiguous coherent allocation, which can fail under memory pressure. Firmware failures are returned directly. The driver stores flags in shared manager private data, so callers rely on manager serialization. State reporting ignores errors from `zynqmp_pm_fpga_get_status()`.

## Test signals
Probe, full and partial firmware loads, coherent allocation failure injection, firmware error propagation, sysfs `status` reads, and operating/unknown state transitions from firmware status are key validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/zynqmp-fpga.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fsi/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/fsi/Kconfig

## Purpose
`drivers/fsi/Kconfig` defines the build-time configuration surface for the Linux FSI subsystem and its FSI masters/client drivers in this source tree.

## Important APIs, types, and functions
The top-level `menuconfig FSI` is a tristate depending on OF and selecting CRC4. Child symbols include `FSI_NEW_DEV_NODE`, `FSI_MASTER_GPIO`, `FSI_MASTER_HUB`, `FSI_MASTER_AST_CF`, `FSI_MASTER_ASPEED`, `FSI_MASTER_I2CR`, `FSI_SCOM`, `FSI_SBEFIFO`, `FSI_OCC`, and `I2CR_SCOM`.

## Control flow
Kconfig has no runtime control flow. Build selection controls whether the core, masters, and clients are compiled. `FSI_OCC` depends on `FSI_SBEFIFO`; `I2CR_SCOM` depends on `FSI_MASTER_I2CR`; GPIO and Aspeed ColdFire masters declare GPIO-related dependencies.

## State and persistence behavior
The file controls kernel configuration state only. `FSI_NEW_DEV_NODE` changes runtime device-node naming conventions by selecting `/dev/fsi/...` paths and shifted numbering, but the option itself is build-time state.

## Dependencies and integration points
It integrates with Kbuild via the sibling Makefile and with the broader kernel configuration system. Dependency choices reflect driver requirements: OF enumeration, CRC4 protocol support, GPIOLIB, GPIO_ASPEED, GENERIC_ALLOCATOR, HAS_IOMEM, I2C, and OF_ADDRESS.

## Risks and edge cases
Changing dependencies can produce drivers without required framework support or hide valid hardware. `FSI_NEW_DEV_NODE` affects userspace ABI expectations, so enabling it without updated udev/userspace can break legacy tooling.

## Test signals
Configuration matrix builds with core-only, each master, SBEFIFO/OCC, and I2CR combinations are the primary signals. Runtime checks should verify device-node paths under both legacy and new dev-node modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fsi/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fsi/Makefile -->
# sources/distributed-fs/ceph-client/drivers/fsi/Makefile

## Purpose
`drivers/fsi/Makefile` maps FSI Kconfig symbols to the object files that implement the FSI core, masters, and client drivers.

## Important APIs, types, and functions
It builds `fsi-core.o` for `CONFIG_FSI`, master objects for hub, ASPEED, GPIO, I2CR, and AST ColdFire options, and client objects for SCOM, SBEFIFO, OCC, and I2CR SCOM.

## Control flow
There is no runtime control flow. Kbuild includes each object based on the corresponding `CONFIG_*` symbol.

## State and persistence behavior
The file has build-time state only and does not participate in runtime persistence.

## Dependencies and integration points
It integrates with the Kconfig file in the same directory and the kernel Kbuild system. The object list defines which modules or built-ins are produced for each enabled symbol.

## Risks and edge cases
Object names must remain aligned with source files and Kconfig symbols. Missing an object here causes selected drivers not to build; stale entries cause link failures.

## Test signals
Build tests for each tristate as built-in and module should verify expected `.o` inclusion and absence of unresolved symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fsi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fsi/cf-fsi-fw.h -->
# sources/distributed-fs/ceph-client/drivers/fsi/cf-fsi-fw.h

## Purpose
`cf-fsi-fw.h` defines the ABI between the ARM-side Aspeed ColdFire FSI master driver and the ColdFire microcode image `cf-fsi-fw.bin`. It documents firmware header layout, boot configuration offsets, SRAM command/status registers, response fields, GPIO arbitration, and trace-buffer encodings.

## Important APIs, types, and functions
Important definitions include `HDR_OFFSET`, firmware signatures `SYS_SIG_SHARED` and `SYS_SIG_SPLIT`, API version `2.1`, boot config offsets for command/status area and GPIO virtual/data registers, command constants `CMD_COMMAND`, `CMD_BREAK`, `CMD_IDLE_CLOCKS`, status values such as `STAT_COMPLETE` and `STAT_ERR_MTOE`, SRAM offsets `CMD_DATA`, `RSP_DATA`, `ARB_REG`, and trace constants under `TRACEBUF`.

## Control flow
The header has no executable flow. `fsi-master-ast-cf.c` uses it to locate a matching firmware image, patch GPIO and control fields before starting the coprocessor, write command/status words in SRAM, decode completion/error status, arbitrate GPIO access, and optionally dump microcode traces.

## State and persistence behavior
It describes runtime memory shared between the host CPU and ColdFire firmware. Firmware image headers persist in the firmware blob, while SRAM command/status fields are transient and cleared/rewritten during setup and command execution.

## Dependencies and integration points
It is included by `fsi-master-ast-cf.c` and tightly coupled to `cf-fsi-fw.bin`. The register contract also integrates with Aspeed SRAM, SCU ColdFire mapping, GPIO coprocessor arbitration, and optional CVIC doorbells.

## Risks and edge cases
Offsets and status encodings are firmware ABI. Any mismatch between this header and the loaded firmware can break command submission, GPIO ownership, or trace interpretation. API major-version checks in the driver are the main guard.

## Test signals
ColdFire firmware load with both shared and split GPIO signatures, API-version validation, command/status completion, GPIO arbitration, and trace dump decoding validate this header's contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fsi/cf-fsi-fw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fsi/fsi-core.c -->
# sources/distributed-fs/ceph-client/drivers/fsi/fsi-core.c

## Purpose
`fsi-core.c` implements the Linux FSI bus core. It registers the FSI bus and master class, exposes endpoint read/write helpers, discovers CFAM slaves and engines, manages slave character devices, allocates minors for FSI client cdevs, handles bus error recovery, and provides master/driver registration APIs.

## Important APIs, types, and functions
Exported APIs include `fsi_device_read()`, `fsi_device_write()`, `fsi_device_peek()`, `fsi_slave_read()`, `fsi_slave_write()`, `fsi_slave_claim_range()`, `fsi_slave_release_range()`, `fsi_get_new_minor()`, `fsi_free_minor()`, `fsi_master_rescan()`, `fsi_master_register()`, `fsi_master_unregister()`, `fsi_driver_register()`, and `fsi_driver_unregister()`. Core internal flows include `fsi_slave_init()`, `fsi_slave_scan()`, `fsi_slave_handle_error()`, `fsi_master_scan()`, and CFAM cdev operations `cfam_read()`/`cfam_write()`.

## Control flow
Postcore init allocates a character-device major, registers the FSI bus, and registers the FSI master class. A hardware master calls `fsi_master_register()`, receives an ID, registers its master device, and unless `no-scan-on-init` is set, scans each link. Scanning enables a link, sends a break, reads CFAM ID zero, validates CRC4, creates a slave device, configures async mode if the master software-clocks the bus, forces LBUS ownership, programs SMODE, allocates a CFAM minor/cdev, applies link delay config, creates a legacy raw sysfs file, and scans the engine table. Engine-table entries with valid CRC, type, and slots become `struct fsi_device` children matched to FSI client drivers.

Bus access enters through `fsi_device_read/write()` or CFAM/raw file ops, validates bounds and alignment, calls `fsi_slave_read/write()`, encodes 23-bit addresses through slave ID when needed, and retries after `fsi_slave_handle_error()`. Error handling first reports/clears slave status, then optionally sends TERM and probes communication, and finally sends BREAK, restores delays, reprograms SMODE, and calls the master's `link_config`. Master rescan unscans all child slaves/devices under `scan_lock` before scanning again.

## State and persistence behavior
Global runtime state includes `master_ida`, `fsi_minor_ida`, `fsi_base_dev`, and the `discard_errors` module parameter. Each master owns scan state and link callbacks; each slave stores CFAM ID, chip ID, link/id, size, cdev/minor, send/echo delays, OF node, and parent master. No durable persistence exists, but minor numbering preserves legacy ABI where possible and OF aliases can force stable client numbering.

## Dependencies and integration points
The file depends on CRC4, device/bus/class core, IDA allocation, OF matching/address data, cdev/fs/uaccess, tracepoints, `fsi-master.h`, and `fsi-slave.h`. It integrates upward with FSI client drivers through `struct fsi_driver` and downward with hardware-specific masters through `struct fsi_master` callbacks.

## Risks and edge cases
Important risks include 23-bit address encoding only working for slave ID zero, engine-table CRC/slot parsing errors, userspace ABI differences under `CONFIG_FSI_NEW_DEV_NODE`, retry/error recovery loops that can hide persistent bus faults, and lifetime rules where `fsi_master_register()` takes ownership of `master->dev`. `fsi_slave_claim_range()` currently does not check overlaps, so hub address reservations are advisory.

## Test signals
Signals include bus/master class registration, master scan with valid/invalid CFAM CRC, engine discovery and OF node matching, CFAM char-device reads/writes with unaligned offsets, raw sysfs access sizing, TERM/BREAK recovery paths, minor allocation with legacy and alias numbering, driver match/probe/remove, and rescan/unregister cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fsi/fsi-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fsi/fsi-master-aspeed.c -->
# sources/distributed-fs/ceph-client/drivers/fsi/fsi-master-aspeed.c

## Purpose
`fsi-master-aspeed.c` is the AST2600 hardware FSI master driver. It accesses the FSI controller through an OPB bridge, initializes the embedded hub master, exposes FSI master callbacks to the core, and supports optional board-level CFAM reset and Tacoma external-cable muxing.

## Important APIs, types, and functions
`struct fsi_master_aspeed` embeds `struct fsi_master` and stores lock, device, OPB MMIO base, clock, and optional CFAM reset GPIO. Low-level helpers are `__opb_read()`, `__opb_write()`, typed OPB accessors, and `check_errors()`. Master callbacks are `aspeed_master_read()`, `aspeed_master_write()`, `aspeed_master_link_enable()`, `aspeed_master_term()`, and `aspeed_master_break()`. Probe initializes hardware in `aspeed_master_init()`.

## Control flow
Probe applies optional cable mux fixup, allocates state, maps OPB registers, enables the clock, sets optional CFAM reset sysfs, configures OPB interrupt masks, retry counter, controller/FSI base windows, read/write data ordering, selects OPB0, reads `FSI_MVER` for link count, fills `struct fsi_master`, initializes the controller, registers the master, and takes an extra device reference for remove. Read/write callbacks validate ID, encode ID into address bits and link into hub link offset, serialize OPB access under `lock`, perform byte/halfword/fullword transfers, and clear master errors on `-EIO`. Link enable writes `MSENP0` or `MCENP0` and delays for setup.

## State and persistence behavior
Runtime state is MMIO configuration, enabled clock, optional GPIO state, the bus divisor module parameter `bus_div`, and the master object. No persistent storage exists. Hardware initialization programs FSI MMODE, delays, error control, link enable masks, and bridge resets.

## Dependencies and integration points
It depends on platform/OF matching `aspeed,ast2600-fsi-master`, clocks, MMIO, GPIO descriptors, tracepoints, mutexes, and the FSI core master API. Optional board integration uses `fsi-routing` and `fsi-mux` GPIOs plus `cfam-reset`.

## Risks and edge cases
OPB polling has a short timeout and synchronous error handling. The driver currently selects OPB0 for all operations and notes future work for OPB1/DMA. Global `aspeed_fsi_divisor` can be altered by cable fixup unless module parameters override it. Remove does not drop the extra master device reference directly in this file, so lifetime depends on core unregister/release behavior.

## Test signals
Probe with OPB resource/clock, hub version/link count read, FSI scans across reported links, byte/halfword/word transfers, OPB timeout and `STATUS_ERR_ACK` handling, CFAM reset sysfs action, cable mux divisor change, and unregister cleanup validate this driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fsi/fsi-master-aspeed.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fsi/fsi-master-ast-cf.c -->
# sources/distributed-fs/ceph-client/drivers/fsi/fsi-master-ast-cf.c

## Purpose
`fsi-master-ast-cf.c` implements an FSI master using the ColdFire coprocessor present in AST2400/AST2500 BMCs. It loads `cf-fsi-fw.bin` into reserved memory, patches firmware boot configuration, arbitrates GPIO ownership with the Aspeed GPIO driver, communicates with microcode through SRAM command/status registers, and exposes one FSI link to the core.

## Important APIs, types, and functions
`struct fsi_master_acf` stores the embedded master, SCU regmap, GPIOs and coprocessor GPIO metadata, reserved firmware memory, CVIC mapping, SRAM pool allocation, AST generation flag, external-mode flag, last-address cache, delays, and trace flag. Command construction mirrors the GPIO master with `build_ar_command()`, `build_dpoll_command()`, `build_epoll_command()`, and `build_term_command()`. Coprocessor operations use `do_copro_command()`, `send_request()`, `read_copro_response()`, `handle_response()`, and `fsi_master_acf_xfer()`. Setup/lifecycle functions include `load_copro_firmware()`, `check_firmware_image()`, `fsi_master_acf_setup()`, `fsi_master_acf_terminate()`, and probe/remove.

## Control flow
Probe resolves AST generation, SCU regmap, GPIOs, reserved DRAM, optional CVIC, fixed SRAM allocation, and GPIO coprocessor arbitration hooks. Setup resets ColdFire, clears SRAM, assigns GPIOs to the coprocessor, loads the matching shared/split firmware image, verifies firmware API major version, configures AST-specific memory maps and firmware GPIO/control fields, starts ColdFire, waits for `CF_STARTED`, writes send/echo delays, enables CVIC doorbell when available, then registers the FSI master. Access callbacks build FSI protocol commands, send them to SRAM, ring the coprocessor doorbell, wait for completion, validate CRC, handle ACK/BUSY/ERRA/ERRC, issue D_POLL/E_POLL/TERM as needed, update the last-address optimization, and return data in bus endian format.

## State and persistence behavior
Runtime state spans driver memory, firmware DRAM, SRAM command/status fields, SCU ColdFire mapping registers, GPIO ownership, and last-address/delay caches. The firmware blob is external persistent input, but the driver writes it into reserved memory on setup. External mode stops the coprocessor, returns GPIOs to ARM/external ownership, rescans the bus, and can later restart setup.

## Dependencies and integration points
The driver depends on CRC4, firmware loader, OF reserved memory, genalloc SRAM pools, SCU syscon regmap, Aspeed GPIO coprocessor APIs, optional CVIC, GPIO descriptors, tracepoints, and FSI master APIs. It uses the ABI constants in `cf-fsi-fw.h` and declares `MODULE_FIRMWARE("cf-fsi-fw.bin")`.

## Risks and edge cases
Firmware/header ABI mismatch, reserved-memory alignment, fixed SRAM offset allocation, GPIO arbitration races at startup/shutdown, and coprocessor command timeouts are major risks. Error handling can dump firmware trace data only when trace-enabled firmware is loaded. The last-address optimization must be invalidated on failures, TERM, and BREAK. External mode transitions must serialize against in-flight commands.

## Test signals
Validation should cover AST2400 and AST2500 probe, firmware image selection for shared/split GPIOs, API-version rejection, CVIC interrupt enable, read/write/TERM/BREAK transfers, BUSY and CRC retry paths, external-mode toggling with rescan, GPIO arbitration request/release, and cleanup releasing SRAM and coprocessor GPIOs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fsi/fsi-master-ast-cf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fsi/fsi-master-gpio.c -->
# sources/distributed-fs/ceph-client/drivers/fsi/fsi-master-gpio.c

## Purpose
`fsi-master-gpio.c` is a software bit-banged FSI master using GPIO lines. It serializes FSI protocol commands over clock/data/translator GPIOs, implements response parsing and retry behavior, and registers a single-link software-clocked master with the FSI core.

## Important APIs, types, and functions
`struct fsi_master_gpio` stores the embedded master, GPIO descriptors, command lock, external-mode flag, delay settings, and last-address cache. Protocol helpers include `serial_out()`, `serial_in()`, `clock_zeros()`, `msg_push_crc()`, `build_ar_command()`, `build_dpoll_command()`, `build_epoll_command()`, `read_one_response()`, `poll_for_response()`, and `fsi_master_gpio_xfer()`. Master callbacks are `fsi_master_gpio_read()`, `fsi_master_gpio_write()`, `fsi_master_gpio_term()`, `fsi_master_gpio_break()`, `fsi_master_gpio_link_enable()`, and `fsi_master_gpio_link_config()`.

## Control flow
Probe acquires mandatory clock/data GPIOs and optional trans/enable/mux GPIOs, sets default send/echo delays, marks the master as software-clocked, initializes GPIO output mode, creates `external_mode` sysfs, and registers the master. Reads and writes serialize on `cmd_lock`, build absolute/relative/same-address commands depending on `last_addr`, bit-bang the command with interrupts disabled around timing-sensitive serial I/O, wait through echo/send delays, parse ACK/BUSY/ERRA/ERRC responses, issue D_POLL or E_POLL retries, and update the last-address cache. BREAK clocks the protocol break sequence and invalidates the cache.

## State and persistence behavior
State is runtime-only: GPIO directions/values, `external_mode`, `last_addr`, and delay values. `external_mode` switches GPIOs to input/external mux mode and rescans the master; switching back reinitializes the bit-banged bus.

## Dependencies and integration points
It depends on GPIO descriptors, CRC4, IRQ flag helpers, delays, OF platform binding `fsi-master-gpio`, tracepoints, and the FSI master API. The FSI core uses its callbacks as a normal master and configures slave delays through `link_config`.

## Risks and edge cases
Timing is CPU/GPIO-controller dependent; `no-gpio-delays` improves AST2500 performance but can be unsafe elsewhere. The implementation disables local IRQs for serial segments but still relies on GPIO operations not sleeping. It supports only link 0. Response CRC retry and busy handling must avoid confusing command CRC errors with transport loss. Optional GPIOs must be present in practice for boards that need mux/translator control.

## Test signals
Signals include probe with and without optional GPIOs, FSI scan on link 0, reads/writes of 1/2/4 bytes, same/relative address command selection, CRC retry paths, BUSY D_POLL behavior, BREAK and TERM recovery, external-mode toggling, and timing behavior with `no-gpio-delays`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fsi/fsi-master-gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fsi/fsi-master-hub.c -->
# sources/distributed-fs/ceph-client/drivers/fsi/fsi-master-hub.c

## Purpose
`fsi-master-hub.c` implements a cascaded FSI hub master discovered as an FSI engine. The hub exposes downstream links through an address window on an upstream FSI slave and registers a new `struct fsi_master` for those downstream links.

## Important APIs, types, and functions
`struct fsi_master_hub` embeds `struct fsi_master`, stores the upstream `fsi_device`, and records the slave-relative link-window address and size. Master callbacks are `hub_master_read()`, `hub_master_write()`, `hub_master_break()`, and `hub_master_link_enable()`. `hub_master_init()` programs hub master registers, and `hub_master_probe()`/`hub_master_remove()` bind through an FSI driver for engine type `0x1c`.

## Control flow
Probe reads `FSI_MVER` from the upstream device to determine link count, claims the downstream address range starting at `FSI_HUB_LINK_OFFSET`, allocates hub state, initializes common hub registers, registers a new FSI master, and takes an extra device reference. Downstream reads/writes reject nonzero slave IDs, translate link-local addresses to `hub->addr + link * FSI_HUB_LINK_SIZE + addr`, and call `fsi_slave_read/write()` on the upstream slave. Link enable writes `MSENP0` or `MCENP0`; break writes the magic break word through the translated write path.

## State and persistence behavior
The hub stores upstream device and address-window metadata plus the registered master object. Hardware state is in hub master registers and link enable masks. There is no persistence beyond runtime device state.

## Dependencies and integration points
It depends on the FSI core's client and master APIs, common master register constants from `fsi-master.h`, CRC/error behavior in the core, and FSI engine discovery. It bridges upstream FSI access into a nested master scan.

## Risks and edge cases
Only slave ID zero is supported on downstream links. `fsi_slave_claim_range()` does not enforce overlap today, weakening protection against conflicting clients. Initialization errors after allocation must release the claimed range. Link count from hardware controls the reserved address size, so malformed `MVER` can cause incorrect range assumptions.

## Test signals
Engine discovery for type `0x1c`, hub version/link count read, downstream master scan, translated read/write correctness per link, link enable/disable writes, break handling, and remove cleanup of range and master references are core signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fsi/fsi-master-hub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fsi/fsi-master-i2cr.c -->
# sources/distributed-fs/ceph-client/drivers/fsi/fsi-master-i2cr.c

## Purpose
`fsi-master-i2cr.c` implements a virtual FSI master behind an IBM I2C Responder (I2CR). The I2CR translates I2C transactions into CFAM/SCOM-style access, so the driver emulates enough CFAM configuration space for FSI engine discovery and forwards engine accesses over I2C.

## Important APIs, types, and functions
Shared exported helpers are `fsi_master_i2cr_read()` and `fsi_master_i2cr_write()`. Internal helpers include parity functions `i2cr_check_parity32()`, `i2cr_check_parity64()`, command builder `i2cr_get_command()`, transaction helper `i2cr_transfer()`, and status checker `i2cr_check_status()`. Master callbacks are `i2cr_read()` and `i2cr_write()`.

## Control flow
Probe allocates `struct fsi_master_i2cr`, chooses a stable master index from the I2C adapter number, initializes a one-link master, and registers it with the FSI core. Core reads below `0xc00` are served from the static `i2cr_cfam` table so the core can discover engines; writes in that range are successful no-ops. Other accesses build parity-protected I2CR commands from CFAM word addresses, perform I2C write/read or write-only transfers under a mutex, check I2CR status/error/log registers, clear error state by writing zeroed command buffers, and convert between FSI big-endian byte expectations and I2CR little-endian wire layout.

## State and persistence behavior
Runtime state is the I2C client pointer, mutex, and registered FSI master. `i2cr_cfam` is static emulated configuration data. I2CR status/error/log registers are cleared after error detection, but no state persists in the driver.

## Dependencies and integration points
It depends on I2C core, OF match `ibm,i2cr-fsi-master`, tracepoints, `fsi-master-i2cr.h`, and FSI master registration. Its exported helpers are also consumed by I2CR-specific clients such as direct I2CR SCOM support.

## Risks and edge cases
The virtual master supports only link 0, slave ID 0, 16-bit local addresses, and 1/2/4 byte accesses. The fake CFAM table must stay consistent with expected FSI discovery behavior. Parity and endian conversions are subtle; mistakes can produce remote I2CR errors. Error clearing uses best-effort I2C sends after status failure.

## Test signals
Probe on an I2C adapter, FSI scan through emulated CFAM space, reads/writes above `0xc00`, parity validation, endian round-trips, status-error trace/log collection, and remove/unregister behavior are important signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fsi/fsi-master-i2cr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fsi/fsi-master-i2cr.h -->
# sources/distributed-fs/ceph-client/drivers/fsi/fsi-master-i2cr.h

## Purpose
`fsi-master-i2cr.h` defines the shared structure and helper prototypes for the IBM I2C Responder virtual FSI master.

## Important APIs, types, and functions
`struct fsi_master_i2cr` embeds `struct fsi_master`, stores a mutex protecting hardware access, and stores the backing `struct i2c_client`. It declares `fsi_master_i2cr_read()` and `fsi_master_i2cr_write()`, and provides `to_fsi_master_i2cr()` plus `is_fsi_master_i2cr()`.

## Control flow
The header has no executable control flow except the inline type check, which identifies I2CR-backed masters by testing whether the master parent device is an I2C client.

## State and persistence behavior
It describes runtime-only state shared by I2CR master and client code. There is no persistent data.

## Dependencies and integration points
It depends on I2C, mutexes, and `fsi-master.h`. It is the boundary between the I2CR master implementation and other drivers that can perform direct I2CR operations.

## Risks and edge cases
`is_fsi_master_i2cr()` is structural rather than type-tag based, so it assumes parent device type is sufficient. Callers must hold no assumptions about locking beyond using exported helpers, which serialize on `lock`.

## Test signals
Build coverage, direct helper calls from I2CR consumers, and correct identification of I2CR masters validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fsi/fsi-master-i2cr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fsi/fsi-master.h -->
# sources/distributed-fs/ceph-client/drivers/fsi/fsi-master.h

## Purpose
`fsi-master.h` defines the contract between the FSI core and hardware-specific FSI masters. It also centralizes common FSI master register offsets, register bitfields, hub address geometry, protocol timing constants, command/response encodings, retry limits, and master lifecycle APIs.

## Important APIs, types, and functions
The central type is `struct fsi_master`, which embeds a `struct device`, master index, link count, flags, `scan_lock`, and callbacks for read, write, term, send_break, link_enable, and link_config. Public functions are `fsi_master_register()`, `fsi_master_unregister()`, and `fsi_master_rescan()`. Constants include `FSI_MMODE`, `FSI_MRESP0`, `FSI_MRESB0`, command opcodes like `FSI_CMD_ABS_AR`, response tags like `FSI_RESP_ACK`, and `FSI_MASTER_FLAG_SWCLOCK`.

## Control flow
The header itself has no executable flow. Hardware masters populate a `struct fsi_master`, set callbacks and device release behavior, then hand it to the core. The core invokes callbacks during scan, read/write, error recovery, link enable/disable, delay configuration, TERM, and BREAK.

## State and persistence behavior
It defines runtime structures and register constants only. Master lifetime comments document that registration takes ownership of `master->dev` and that implementations may need an extra reference if remove paths need to access the object after unregister.

## Dependencies and integration points
It depends on device and mutex APIs. All FSI master drivers in this subset include it, and `fsi-core.c` uses it as the core-to-master ABI.

## Risks and edge cases
The lifetime rules are easy to get wrong because `fsi_master_unregister()` can drop the final device reference. Register constants are shared by hardware and hub masters, so incorrect bit definitions affect multiple drivers. Protocol retry constants influence GPIO and ColdFire behavior.

## Test signals
Build coverage of all masters, registration/unregistration lifetime tests, scan/rescan flows, and callback invocation under error recovery validate the interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fsi/fsi-master.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fsi/fsi-occ.c -->
# sources/distributed-fs/ceph-client/drivers/fsi/fsi-occ.c

## Purpose
`fsi-occ.c` implements the FSI/SBEFIFO-backed On-Chip Controller interface for POWER systems. It exposes an `occN` miscdevice, submits OCC commands through SBEFIFO SRAM get/put commands, validates OCC responses and checksums, saves FFDC on failures, and creates an `occ-hwmon` child device.

## Important APIs, types, and functions
`struct occ` stores the parent devices, index/name, version, sequence number, shared buffers, miscdevice, and `occ_lock`. `struct occ_client` stores per-open buffers and read offsets. The exported command API is `fsi_occ_submit()`. SRAM helpers are `occ_getsram()`, `occ_putsram()`, and `occ_trigger_attn()`. Userspace file ops are `occ_open()`, `occ_write()`, `occ_read()`, and `occ_release()`.

## Control flow
Probe allocates a shared SBE response buffer, determines P9/P10 mode from OF match data, seeds a nonzero sequence number, allocates an OCC index, registers `/dev/occN`, and creates an OF or platform `occ-hwmon` child. A userspace write copies an OCC-format command into the per-client buffer, computes the command data length, and calls `fsi_occ_submit()`. Submission serializes on `occ_lock`, overwrites the request sequence number, computes checksum, writes the command to OCC SRAM through SBEFIFO, triggers OCC attention, polls the response header until status/sequence/cmd match or timeout, fetches the full response, validates response size and checksum, stores final response length, and returns it for later reads.

## State and persistence behavior
Runtime state includes the OCC sequence counter, per-device shared SBE buffer, per-client buffers/read offsets, and temporary FFDC copies into the caller's response buffer. No persistent state exists. Remove deregisters the miscdevice, nulls/frees the shared buffer under lock, removes child hwmon devices, and frees the IDA index.

## Dependencies and integration points
It depends on platform devices, OF matching `ibm,p9-occ` and `ibm,p10-occ`, miscdevice/fs/uaccess APIs, SBEFIFO exported APIs `sbefifo_submit()` and `sbefifo_parse_status()`, OCC UAPI constants, IDA allocation, and optional hwmon child creation.

## Risks and edge cases
Sequence-number uniqueness is critical because stale OCC responses can otherwise be accepted. Request/response length checks must account for OCC headers and two-byte checksums. P9 and P10 SRAM command formats differ by mode/address fields. Timeouts and command-in-progress statuses require careful polling without holding user locks incorrectly. Remove must prevent use after free by setting `occ->buffer = NULL` under `occ_lock`.

## Test signals
Signals include miscdevice open/write/read/release, P9 and P10 SRAM command formatting, checksum mismatch rejection, response timeout, stale sequence/cmd filtering, FFDC capture on SBE status errors, response-size overflow, hwmon child creation/removal, and concurrent clients serialized through `occ_lock`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fsi/fsi-occ.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fsi/fsi-sbefifo.c -->
# sources/distributed-fs/ceph-client/drivers/fsi/fsi-sbefifo.c

## Purpose
`fsi-sbefifo.c` provides the Linux device interface to the POWER Self Boot Engine FIFO. It registers an FSI client for SBEFIFO engines, exposes a character device for userspace command/response transactions, exports in-kernel `sbefifo_submit()` and `sbefifo_parse_status()`, handles FIFO cleanup/reset, timeout reporting, SBE state checks, and FFDC collection.

## Important APIs, types, and functions
`struct sbefifo` stores magic, FSI device, cdev device, lock, broken/dead/async-FFDC/timeout flags, and active timeout settings. `struct sbefifo_user` stores per-file command staging and timeout overrides. Exported functions are `sbefifo_submit()` and `sbefifo_parse_status()`. Core hardware helpers include `sbefifo_check_sbe_state()`, `sbefifo_request_reset()`, `sbefifo_cleanup_hw()`, `sbefifo_wait()`, `sbefifo_send_command()`, `sbefifo_read_response()`, `sbefifo_do_command()`, and `__sbefifo_submit()`.

## Control flow
Probe allocates the SBEFIFO object, takes a reference on the FSI device, allocates a source-tree FSI minor, registers `sbefifoN`, creates OF platform children such as OCC, and exposes a read-only `timeout` attribute. Kernel clients call `sbefifo_submit()`, which builds a kernel iov iterator, locks the FIFO, validates command length, cleans hardware, optionally collects async FFDC, sends the command into the UP FIFO with EOT, reads DOWN FIFO words until EOT, resets on failures, and returns response word count. Userspace writes stage one command, except the magic `"RSET"` word triggers reset immediately; a later read executes the staged command into the user buffer. Ioctls adjust command and read timeouts per open file.

## State and persistence behavior
State is runtime-only. `broken` forces reset before reuse, `dead` rejects submissions during removal, `async_ffdc` tracks mailbox-reported asynchronous FFDC, and `timed_out` is exposed through sysfs with notifications. Per-open staged commands can be page-backed or vmalloc-backed and are released after read or close.

## Dependencies and integration points
It depends on the FSI device APIs, FSI cdev minor helpers, OF child platform creation, cdev/fs/uaccess/uio iterators, vmalloc, SBEFIFO UAPI ioctls, and SBE/OCC command constants. `fsi-occ.c` uses its exported submission/status parsing helpers.

## Risks and edge cases
FIFO reset and cleanup are central: parity errors, non-empty FIFOs, EOT acknowledgement failures, SBE reset requests, and timeouts all need to leave the next command safe. Response overflow returns `-EOVERFLOW` while still draining to EOT. `sbefifo_parse_status()` returns positive SBE primary status values distinct from Linux errors. Userspace depends on `-EAGAIN` when reading without a staged command. Concurrency is serialized by the device lock plus per-file locks.

## Test signals
Signals include probe/minor allocation, userspace write-then-read transactions, reset magic handling, ioctl timeout changes, kernel `sbefifo_submit()` response length accounting, status parsing with FFDC, async FFDC retrieval, FIFO parity/reset/timeout paths, response overflow, SBE state rejection, child OCC creation/removal, and dead-device rejection during remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fsi/fsi-sbefifo.c -->
