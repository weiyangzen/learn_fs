# subset-b-005194 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-qcom-pdc.c -->
# sources/distributed-fs/ceph-client/drivers/reset/reset-qcom-pdc.c

Purpose: Qualcomm PDC global reset controller for SDM845 and SC7280, exposing PDC synchronous reset bits through the reset-controller framework.

Important APIs/types/functions: `qcom_pdc_reset_map`, `qcom_pdc_reset_desc`, and `qcom_pdc_reset_data` describe binding IDs, per-SoC register offsets, and the controller instance. `qcom_pdc_control_assert()` and `qcom_pdc_control_deassert()` use `regmap_update_bits()` against the selected PDC sync-reset register. `qcom_pdc_reset_probe()` maps MMIO, initializes a 32-bit regmap, gets OF match data, and registers `qcom_pdc_reset_ops`.

Control flow: compatible matching selects the descriptor, probe maps the single resource and registers `nr_resets` equal to the SoC reset table length. Consumers call reset core operations, which translate IDs into table bits and set or clear the matching register bit.

State and persistence: no persisted software state beyond the regmap and descriptor pointer; hardware reset bits hold current state. Device-managed allocation and registration own cleanup.

Dependencies and integration: depends on platform device probing, OF compatible strings, `dt-bindings/reset/qcom,sdm845-pdc.h`, MMIO regmap, and reset-controller consumers in device tree.

Risks and test signals: operations trust the reset core to keep `idx < nr_resets`; sparse binding tables would make holes unsafe. Test with SDM845 and SC7280 DT bindings, invalid IDs through reset-core tests, regmap failure injection, and checking that assert/deassert touches only the expected offset and bit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-qcom-pdc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-raspberrypi.c -->
# sources/distributed-fs/ceph-client/drivers/reset/reset-raspberrypi.c

Purpose: Raspberry Pi firmware reset provider, currently implementing the Pi 4 VL805/xHCI reset notification through VideoCore firmware.

Important APIs/types/functions: `struct rpi_reset` stores the reset controller and firmware handle. `rpi_reset_reset()` handles `RASPBERRYPI_FIRMWARE_RESET_ID_USB`, builds the hardwired PCI device address, calls `rpi_firmware_property(... RPI_FIRMWARE_NOTIFY_XHCI_RESET ...)`, and delays for VL805 startup. `rpi_reset_probe()` finds the parent firmware node, gets `struct rpi_firmware`, and registers `rpi_reset_ops`.

Control flow: probe defers until firmware is available, then exposes `RASPBERRYPI_FIRMWARE_RESET_NUM_IDS`. Consumers issue a reset pulse; unsupported IDs return `-EINVAL`.

State and persistence: only runtime firmware handle state exists. The reset itself delegates persistent hardware sequencing and optional VL805 firmware loading to VideoCore.

Dependencies and integration: integrates OF platform probing, the Raspberry Pi firmware mailbox API, reset-controller consumers, and `raspberrypi,firmware-reset` bindings.

Risks and test signals: the PCI address is hardcoded for Pi 4 topology and would be wrong for different wiring. Firmware call failures propagate directly. Test signals include probe deferral without firmware, USB reset success on Pi 4, unsupported-ID rejection, and xHCI recovery after PCI reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-raspberrypi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-rzg2l-usbphy-ctrl.c -->
# sources/distributed-fs/ceph-client/drivers/reset/reset-rzg2l-usbphy-ctrl.c

Purpose: Renesas RZ/G2L USB PHY control driver exposing two port resets, keeping the USB PHY PLL/reset register initialized, and creating an auxiliary VBUS regulator platform device.

Important APIs/types/functions: `struct rzg2l_usbphy_ctrl_priv` owns `rcdev`, parent reset, MMIO base, runtime PM, `pwrrdy` syscon field, child `vdev`, and a spinlock. Reset ops update `RESET` bits for port 1/2 and PLL reset. `rzg2l_usbphy_ctrl_pwrrdy_init()` optionally uses the `renesas,sysc-pwrrdy` phandle. PM hooks assert/deassert the parent reset and power-ready state.

Control flow: probe maps MMIO, creates a regmap for `VBENCTL`, enables optional power-ready, deasserts the parent reset, resumes runtime PM, initializes PLL/port resets asserted, registers two reset lines, then registers `rzg2l-usb-vbus-regulator`. Remove and suspend tear down child device, PM, and parent reset in reverse.

State and persistence: reset register bits and optional system-controller power-ready bit hold hardware state. Runtime PM and the child platform device are transient device-managed state.

Dependencies and integration: uses platform MMIO, reset framework, `reset_control`, runtime PM, syscon regmap fields, and Renesas USB PHY/USB VBUS regulator bindings.

Risks and test signals: suspend warns if either PHY reset is deasserted, so consumers must quiesce before suspend. Power-ready phandle masks must be one bit. Test probe error paths, suspend/resume with asserted resets, optional `r9a08g045` power-ready support, and child regulator creation/removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-rzg2l-usbphy-ctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-rzv2h-usb2phy.c -->
# sources/distributed-fs/ceph-client/drivers/reset/reset-rzv2h-usb2phy.c

Purpose: Renesas RZ/V2H(P) USB2 PHY reset controller for a single reset line, using register sequences and also registering an auxiliary mux device.

Important APIs/types/functions: `rzv2h_usb2phy_reset_of_data` packages init/assert/deassert sequences and status bits. Reset ops call `regmap_multi_reg_write()` for assert/deassert and read the configured status register. `rzv2h_usb2phy_reset_mux_register()` allocates an IDA ID and creates a devm auxiliary device named `vbenctl`.

Control flow: probe maps MMIO to a sleeping regmap, obtains a shared deasserted parent reset, enables runtime PM, installs a PM put action, writes the init sequence, registers one reset provider with zero cells, and creates the auxiliary mux.

State and persistence: hardware registers store reset state; software keeps match-data pointers, regmap, runtime PM reference, and IDA auxiliary IDs. Device-managed actions free IDs and drop PM references.

Dependencies and integration: depends on platform probing, reset controls, runtime PM, regmap sequences, auxiliary bus, and `renesas,r9a09g057-usb2phy-reset`.

Risks and test signals: `status()` ignores `regmap_read()` errors. Sequence ordering and delay values are hardware-sensitive. Test init-sequence programming, assert/deassert status, auxiliary-device creation failure cleanup, PM reference cleanup, and parent reset acquisition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-rzv2h-usb2phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-scmi.c -->
# sources/distributed-fs/ceph-client/drivers/reset/reset-scmi.c

Purpose: ARM SCMI reset protocol bridge that exposes SCMI reset domains to Linux reset consumers.

Important APIs/types/functions: `struct scmi_reset_data` stores `rcdev` and the SCMI protocol handle. `scmi_reset_assert()`, `scmi_reset_deassert()`, and `scmi_reset_reset()` forward directly to `scmi_reset_proto_ops`. `scmi_reset_probe()` obtains protocol ops through `handle->devm_protocol_get()` and registers `nr_resets` from `num_domains_get()`.

Control flow: SCMI bus matching on `SCMI_PROTOCOL_RESET` invokes probe. Runtime reset requests are synchronous SCMI protocol calls to platform firmware.

State and persistence: software state is device-managed; reset state is owned by SCMI firmware/system controller. The file has a file-scope `reset_ops` pointer shared by instances.

Dependencies and integration: requires SCMI core, SCMI reset protocol, OF node from the SCMI device, and reset-controller consumers.

Risks and test signals: the global `reset_ops` assumes compatible protocol ops across instances. Firmware errors propagate to consumers. Test with multiple SCMI transports if supported, absent handle, zero domains, firmware failure paths, and assert/reset/deassert domain calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-scmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-simple.c -->
# sources/distributed-fs/ceph-client/drivers/reset/reset-simple.c

Purpose: generic MMIO bit-per-reset controller used by many simple SoC blocks and exported for early/simple platform-specific drivers.

Important APIs/types/functions: `reset_simple_update()` computes 32-bit bank/bit and writes assert/deassert with `active_low`; `reset_simple_reset()` pulses using optional `reset_us`; `reset_simple_status()` interprets readback using `status_active_low`; exported `reset_simple_ops` is shared. `reset_simple_devdata` supplies register offset, fixed reset count, and polarity for OF compatibles.

Control flow: probe maps one MMIO resource, initializes `reset_simple_data`, applies match data such as SoCFPGA offset or active-low variants, offsets the membase, and registers the controller. Consumers invoke standard reset ops.

State and persistence: software holds membase, spinlock, polarity flags, and pulse width. Hardware register bits persist until changed.

Dependencies and integration: integrates platform device probing, OF match table, `linux/reset/reset-simple.h`, spinlocks, and the reset-controller framework.

Risks and test signals: no local ID guard in ops; reset core must enforce `nr_resets`. `reset_us == 0` makes `.reset` unsupported. Test each compatible’s polarity/offset, concurrent RMW locking, resource-size-derived reset count, and pulse timing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-simple.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-sky1.c -->
# sources/distributed-fs/ceph-client/drivers/reset/reset-sky1.c

Purpose: CIX Sky1 system reset controller, mapping numerous binding reset IDs to syscon/regmap offset-bit pairs for main S5 system-control and FCH reset blocks.

Important APIs/types/functions: `sky1_src_signal` maps offset and bit; `sky1_src_variant` selects signal arrays. `sky1_reset_set()` writes active-low reset bits through `regmap_update_bits()`. `sky1_reset_assert()`, `deassert()`, `reset()`, and `status()` implement reset ops with short sleeps. `sky1_reset_probe()` obtains the syscon regmap with `device_node_to_regmap()`.

Control flow: OF match data selects either `variant_sky1` or `variant_sky1_fch`. Probe registers `nr_resets` from the selected array. Runtime assert clears the bit, deassert sets it, and status reports asserted when the bit is clear.

State and persistence: signal tables are static; regmap bits hold hardware state. No runtime persistence beyond registered controller data.

Dependencies and integration: depends on CIX dt-bindings, syscon/regmap, OF platform probing, and reset-controller consumers.

Risks and test signals: several ops ignore return values from helper/regmap reads, so bus errors can look successful. Binding-array holes would make out-of-range or sparse IDs hazardous. Test both compatibles, active-low polarity, reset pulse delay, regmap failure injection, and DT binding ID coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-sky1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-socfpga.c -->
# sources/distributed-fs/ceph-client/drivers/reset/reset-socfpga.c

Purpose: early Intel/Altera SoCFPGA reset-manager registration using `reset_simple_ops`, plus a dummy platform driver to satisfy device-link probing.

Important APIs/types/functions: `a10_reset_init()` manually allocates `reset_simple_data`, maps the reset manager from OF, applies optional `altr,modrst-offset`, and registers 8 banks of resets with active-low status. `socfpga_reset_init()` scans early `altr,rst-mgr` nodes. The later `reset_socfpga_driver` has a no-op probe.

Control flow: early init registers reset control before normal driver model availability. Later the platform driver binds to the same compatible only to attach a driver to the device node.

State and persistence: early allocations and ioremap are not device-managed and remain for system lifetime. Hardware reset registers retain state.

Dependencies and integration: uses OF address translation, manual memory-region reservation, `reset_simple_ops`, `linux/reset/socfpga.h`, and built-in platform driver registration.

Risks and test signals: if `reset_controller_register()` fails, mapped memory is not unwound. Mismatched early and platform bindings can affect device links. Test early boot reset consumers, missing offset property fallback, duplicate reservation failure, and normal platform-device binding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-socfpga.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-sunplus.c -->
# sources/distributed-fs/ceph-client/drivers/reset/reset-sunplus.c

Purpose: Sunplus SP7021 reset controller using HIWORD mask registers and providing a restart sys-off handler.

Important APIs/types/functions: `sp_resets[]` maps logical IDs to packed register/bit positions. `sp_reset_update()` writes high-word mask plus asserted value; `sp_reset_status()` reads current bit. `sp_restart()` pulses reset ID 0. `sp_reset_probe()` maps MMIO, derives reset count from resource size, registers reset ops, then registers restart priority 192.

Control flow: reset consumers assert/deassert via high-word-mask writes. Restart callback asserts and deasserts reset 0 during system restart.

State and persistence: hardware reset registers hold state; no runtime mutable software state beyond MMIO base and rcdev.

Dependencies and integration: platform MMIO, reset-controller framework, sys-off restart handling, Sunplus compatible `sunplus,sp7021-reset`.

Risks and test signals: `nr_resets` is resource-derived rather than `ARRAY_SIZE(sp_resets)`, so mismatched resource size could expose IDs beyond `sp_resets`. Test DT resource sizing, reset ID coverage, restart behavior, and status polarity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-sunplus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-sunxi.c -->
# sources/distributed-fs/ceph-client/drivers/reset/reset-sunxi.c

Purpose: early Allwinner A31 AHB1 reset-controller registration using the shared simple reset implementation before regular drivers are available.

Important APIs/types/functions: `sunxi_reset_init()` allocates `reset_simple_data`, maps the OF resource manually, initializes `reset_simple_ops`, sets active-low behavior, and registers `size * 8` resets. `sun6i_reset_init()` scans `allwinner,sun6i-a31-ahb1-reset`.

Control flow: architecture init calls `sun6i_reset_init()`, which registers matching early reset providers for consumers needed before device-model probing.

State and persistence: allocation and ioremap are permanent early-boot state; hardware registers hold reset state. There is no cleanup path.

Dependencies and integration: OF address helpers, manual memory reservation, `reset_simple_ops`, and `linux/reset/sunxi.h`.

Risks and test signals: on ioremap failure the requested memory region is not released. No dummy platform driver is provided here, unlike SoCFPGA. Test early consumers, memory reservation conflicts, active-low polarity, and boot on systems with and without the compatible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-sunxi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-tenstorrent-atlantis.c -->
# sources/distributed-fs/ceph-client/drivers/reset/reset-tenstorrent-atlantis.c

Purpose: Tenstorrent Atlantis PRCM auxiliary reset driver for RCPU/LSIO peripheral resets backed by a parent PRCM regmap.

Important APIs/types/functions: `atlantis_reset_data` maps register, bit, and polarity; `atlantis_reset_controller_data` selects the reset table. `atlantis_reset_update()` computes active-low value and writes with `regmap_update_bits()`. `atlantis_reset_probe()` gets the parent regmap and registers reset ops for auxiliary device `atlantis_prcm.rcpu-reset`.

Control flow: parent PRCM creates an auxiliary device; probe binds by auxiliary ID, uses `driver_data` for the table, and registers reset controls. Runtime assert/deassert updates one mapped bit.

State and persistence: static reset tables and parent regmap; hardware bits store state. Device-managed allocation owns the controller.

Dependencies and integration: auxiliary bus, parent regmap, Atlantis clock/reset dt-bindings, reset-controller framework.

Risks and test signals: no local `.status` implementation. Trusts reset core for ID bounds and parent for regmap lifetime. Test auxiliary-device matching, parent regmap absence, active-low polarity, and all binding IDs against table coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-tenstorrent-atlantis.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-th1520.c -->
# sources/distributed-fs/ceph-client/drivers/reset/reset-th1520.c

Purpose: T-HEAD TH1520 reset controller family driver covering top-level, AP, DSP, miscellaneous, VI, and VP reset blocks with per-compatible register maps.

Important APIs/types/functions: `th1520_reset_map` maps binding IDs to register offsets and bit masks; `th1520_reset_data` selects a table and count. `th1520_reset_assert()` clears the mapped bit and `th1520_reset_deassert()` sets it through regmap. Probe maps MMIO, initializes a 32-bit regmap, optionally asserts GPU resets for `thead,th1520-reset`, and registers reset ops.

Control flow: OF match data chooses one of six reset tables. Consumers assert/deassert by ID, which indexes directly into the selected table.

State and persistence: static tables encode hardware layout. Register bits persist in hardware; software only holds regmap, table pointer, and rcdev.

Dependencies and integration: platform MMIO, regmap, `dt-bindings/reset/thead,th1520-reset.h`, and reset-controller consumers.

Risks and test signals: direct sparse-array indexing can access zero-initialized table slots if binding IDs are non-contiguous or invalid but below `nr_resets`. There is no status op. Test every compatible, GPU initialization behavior, table/binding continuity, invalid IDs, and regmap update failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-th1520.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-ti-sci.c -->
# sources/distributed-fs/ceph-client/drivers/reset/reset-ti-sci.c

Purpose: TI System Control Interface reset controller that maps two-cell DT reset specifiers to TI SCI device reset masks.

Important APIs/types/functions: `ti_sci_reset_control` stores `dev_id`, `reset_mask`, and a mutex for read-modify-write. `ti_sci_reset_set()` reads device reset state via TI SCI, modifies the mask, and writes it back. `ti_sci_reset_of_xlate()` allocates a control per reset spec and stores it in an IDR. Probe obtains the TI SCI handle and registers a dynamic reset provider.

Control flow: consumers with `<dev_id reset_mask>` specifiers trigger `of_xlate`, which allocates an ID. Assert/deassert/status look up the IDR entry and call TI SCI device ops.

State and persistence: IDR mappings persist for the device lifetime and are destroyed on remove. Actual reset state is maintained by system firmware.

Dependencies and integration: depends on TI SCI protocol handle, OF reset cells, IDR, mutexes, and reset-controller framework.

Risks and test signals: every unique spec allocates device-managed memory and an IDR entry; repeated translations can grow until remove. Test duplicate spec handling, concurrent set mutex behavior, SCI error propagation, remove cleanup, and malformed reset cells.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-ti-sci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-ti-syscon.c -->
# sources/distributed-fs/ceph-client/drivers/reset/reset-ti-syscon.c

Purpose: TI syscon reset provider whose reset layout is described entirely by the `ti,reset-bits` DT property.

Important APIs/types/functions: `ti_syscon_reset_control` records assert/deassert/status offsets, bits, and flags from `dt-bindings/reset/ti-syscon.h`. Reset ops implement flag-driven set/clear/unsupported semantics. `ti_syscon_reset_probe()` gets parent syscon regmap, parses seven-cell control entries, allocates an array, and registers `nr_resets`.

Control flow: at probe, DT data becomes a fixed table. Consumers index that table; assert/deassert write configured bits and status reads configured status bit with flag polarity.

State and persistence: parsed control array is device-managed. Hardware syscon registers hold reset state.

Dependencies and integration: syscon parent node, regmap, OF property parsing, TI reset flag binding, platform reset-controller framework.

Risks and test signals: malformed properties are rejected only by cell count; semantic validation of bit ranges/flags relies on bindings. Test each flag combination, unsupported assert/deassert/status, parent syscon absence, and big-endian property parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-ti-syscon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-tn48m.c -->
# sources/distributed-fs/ceph-client/drivers/reset/reset-tn48m.c

Purpose: Delta TN48M CPLD reset controller for board-level CPU, MAC, PHY, and PoE reset lines.

Important APIs/types/functions: `tn48m_resets[]` maps binding IDs to bits in `TN48M_RESET_REG`. `tn48m_control_reset()` clears a bit then polls until hardware sets it again, implementing a pulse. `tn48m_control_status()` returns asserted when the bit is clear. Probe obtains the parent regmap and registers `.reset` and `.status` ops.

Control flow: platform child of a regmap-providing CPLD binds, registers six resets, and reset consumers trigger poll-based reset pulses.

State and persistence: parent CPLD register state persists; driver holds parent regmap and rcdev only.

Dependencies and integration: parent device regmap, Delta reset dt-bindings, platform bus, reset framework.

Risks and test signals: `regmap_update_bits()` return value is ignored before polling. Poll timeout is 125 ms. Test parent regmap absence, poll timeout, status polarity, and each binding ID bit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-tn48m.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-tps380x.c -->
# sources/distributed-fs/ceph-client/drivers/reset/reset-tps380x.c

Purpose: reset-controller driver for TI TPS380x voltage supervisor reset GPIOs, currently supporting TPS3801 timing.

Important APIs/types/functions: `tps380x_reset` stores rcdev, reset GPIO, and reset delay. `tps380x_reset_assert()` drives the GPIO active, while `tps380x_reset_deassert()` releases it and sleeps for the maximum reset time. `tps380x_reset_of_xlate()` exposes a single zero-cell reset line.

Control flow: probe gets match timing data, requests `reset` GPIO as initially asserted, sets max delay, and registers one reset. Consumers assert/deassert through GPIO operations that may sleep.

State and persistence: only GPIO output state persists in hardware. Delay data is static per compatible.

Dependencies and integration: GPIO descriptors, OF match data, platform probing, reset-controller framework.

Risks and test signals: no `.reset` pulse op is provided, only assert/deassert. Always waits max delay rather than typ/min. Test GPIO polarity from DT, initial asserted output, deassert delay, missing GPIO, and zero-cell phandle translation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-tps380x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-uniphier-glue.c -->
# sources/distributed-fs/ceph-client/drivers/reset/reset-uniphier-glue.c

Purpose: UniPhier glue-layer reset controller for USB3/AHCI blocks that need associated clocks enabled and upstream resets deasserted before exposing simple active-low reset bits.

Important APIs/types/functions: `uniphier_glue_reset_soc_data` lists required clock/reset names. `uniphier_glue_reset_probe()` maps registers, bulk-gets/enables clocks, registers a cleanup action, bulk-gets shared deasserted resets, initializes `reset_simple_data`, and registers `reset_simple_ops`.

Control flow: OF match data chooses one- or two-name resource sets. Probe prepares dependencies first, then exposes all bits in the mapped resource as active-low reset controls.

State and persistence: clock enable state and shared reset deassertions are runtime-managed by devm actions. Hardware reset bits hold state.

Dependencies and integration: clock framework, reset controls, platform MMIO, `reset_simple_ops`, and UniPhier glue compatible strings.

Risks and test signals: `nr_resets` is based on full resource size, not a binding-specific count. MAX limits are guarded by WARN. Test clock/reset dependency failures, devm clock disable on error, active-low bit behavior, and all compatible resource-name sets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-uniphier-glue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-uniphier.c -->
# sources/distributed-fs/ceph-client/drivers/reset/reset-uniphier.c

Purpose: UniPhier SoC reset controller for system, media I/O, SD, peripheral, and analog amplifier reset blocks using syscon regmaps and SoC-specific ID tables.

Important APIs/types/functions: `uniphier_reset_data` records ID, register, bit, and active-low flag. Macros define active-high and active-low entries with sentinel termination. `uniphier_reset_update()` searches the table and writes the target bit with polarity handling. `uniphier_reset_status()` reads and applies polarity. Probe gets parent syscon regmap and computes `nr_resets` from max ID.

Control flow: compatible match selects a reset table; runtime ops linear-search for the requested binding ID. Unknown IDs log and return `-EINVAL`.

State and persistence: static tables encode layout; parent syscon registers store reset state. Software state is devm allocated.

Dependencies and integration: syscon parent nodes, regmap, many UniPhier OF compatibles, reset-controller framework.

Risks and test signals: linear search supports sparse IDs safely but scales with table length. `val = ~mask` relies on `regmap_write_bits()` masking correctly. Test all compatible/table mappings, unknown IDs, active-low and active-high entries, and parent syscon lookup failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-uniphier.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-zynq.c -->
# sources/distributed-fs/ceph-client/drivers/reset/reset-zynq.c

Purpose: Xilinx Zynq reset controller using the SLCR syscon regmap and a memory resource that describes reset register offset/count.

Important APIs/types/functions: `zynq_reset_data` stores SLCR regmap, rcdev, and base offset. Assert/deassert/status compute bank and bit from reset ID and use `regmap_update_bits()` or `regmap_read()`. Probe obtains the `syscon` phandle and first memory resource, then registers `resource_size / 4 * BITS_PER_LONG` resets.

Control flow: built-in platform driver binds `xlnx,zynq-reset`; consumers index reset bits across banks relative to resource start.

State and persistence: SLCR hardware bits persist; driver state is devm allocated.

Dependencies and integration: syscon phandle, platform resources, regmap, built-in reset provider, OF bindings.

Risks and test signals: `BITS_PER_LONG` makes reset count and bank division architecture-width dependent, while registers are 32-bit. Deassert writes `~BIT(offset)` as value under mask, which relies on mask handling. Test on 32- and 64-bit builds, resource size, syscon lookup failures, and status polarity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-zynq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-zynqmp.c -->
# sources/distributed-fs/ceph-client/drivers/reset/reset-zynqmp.c

Purpose: Xilinx ZynqMP/Versal/Versal Net reset provider that forwards reset operations to platform firmware.

Important APIs/types/functions: `zynqmp_reset_soc_data` supplies base firmware reset ID and number of resets. Assert/deassert/reset call `zynqmp_pm_reset_assert()` with ASSERT, RELEASE, or PULSE. Status calls `zynqmp_pm_reset_get_status()`. `zynqmp_reset_of_xlate()` returns the one-cell reset ID.

Control flow: arch init registers the platform driver early. OF match data selects reset range; consumers pass one-cell IDs that are offset by the SoC base before firmware calls.

State and persistence: no hardware state in driver; firmware owns reset state. Software holds match data and rcdev.

Dependencies and integration: Xilinx firmware interface, OF platform probing, reset-controller framework, arch initcall ordering.

Risks and test signals: `of_xlate()` does not validate `args_count` or range itself. Firmware availability and error mapping are critical. Test invalid reset IDs, firmware unavailable/errors, each compatible reset count, and pulse/assert/release operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-zynqmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/spacemit/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/reset/spacemit/Kconfig

Purpose: Kconfig menu for SpacemiT reset controller support, defining shared common infrastructure and K1/K3 SoC reset drivers.

Important APIs/types/functions: symbols are `RESET_SPACEMIT_COMMON`, `RESET_SPACEMIT_K1`, and `RESET_SPACEMIT_K3`. Common support selects `AUXILIARY_BUS`; K1 depends on `SPACEMIT_K1_CCU`, K3 depends on `SPACEMIT_K3_CCU`, and each selects the common reset code.

Control flow: no runtime flow. Build configuration exposes the menu when `ARCH_SPACEMIT || COMPILE_TEST`; enabling SoC CCU support defaults the matching reset driver to the CCU symbol value.

State and persistence: configuration state controls whether objects are built-in, modular, or absent.

Dependencies and integration: binds reset drivers to the SpacemiT CCU providers that create auxiliary devices and parent regmaps.

Risks and test signals: dependency drift with CCU symbols can produce missing auxiliary devices or link failures. Test allmodconfig, COMPILE_TEST without ARCH_SPACEMIT, built-in vs module combinations, and common symbol selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/spacemit/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/spacemit/Makefile -->
# sources/distributed-fs/ceph-client/drivers/reset/spacemit/Makefile

Purpose: Kbuild mapping for SpacemiT reset modules.

Important APIs/types/functions: builds `reset-spacemit-common.o` for `CONFIG_RESET_SPACEMIT_COMMON`, `reset-spacemit-k1.o` for `CONFIG_RESET_SPACEMIT_K1`, and `reset-spacemit-k3.o` for `CONFIG_RESET_SPACEMIT_K3`.

Control flow: Kbuild selects object files according to Kconfig; runtime behavior lives in the C files.

State and persistence: no runtime state. Build artifacts and module composition are determined by `.config`.

Dependencies and integration: common object exports `spacemit_reset_probe` in namespace `RESET_SPACEMIT`, which K1/K3 import.

Risks and test signals: missing common object or namespace import causes link/module-load failures. Test K1-only, K3-only, both, module, and built-in builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/spacemit/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/spacemit/reset-spacemit-common.c -->
# sources/distributed-fs/ceph-client/drivers/reset/spacemit/reset-spacemit-common.c

Purpose: shared SpacemiT auxiliary reset-controller implementation used by K1 and K3 reset table drivers.

Important APIs/types/functions: `spacemit_reset_update()` selects `ccu_reset_data` by ID, combines assert/deassert masks, and writes the selected value with `regmap_update_bits()`. `spacemit_reset_controller_register()` fills `rcdev`. Exported `spacemit_reset_probe()` converts the auxiliary device to `spacemit_ccu_adev`, obtains its regmap, stores `driver_data`, and registers the controller.

Control flow: SoC-specific auxiliary drivers share this probe; their auxiliary ID carries a `ccu_reset_controller_data` pointer. Runtime assert/deassert updates the configured CCU register masks.

State and persistence: controller state is device-managed; reset bits persist in the parent CCU registers.

Dependencies and integration: auxiliary bus, SpacemiT CCU helper API, regmap, reset-controller framework, and exported namespace `RESET_SPACEMIT`.

Risks and test signals: direct table indexing depends on reset core ID bounds and contiguous binding arrays. Test parent regmap lifetime, assert/deassert mask combinations, namespace import, and auxiliary driver data correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/spacemit/reset-spacemit-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/spacemit/reset-spacemit-common.h -->
# sources/distributed-fs/ceph-client/drivers/reset/spacemit/reset-spacemit-common.h

Purpose: shared type and macro contract for SpacemiT CCU-backed reset controllers.

Important APIs/types/functions: defines `ccu_reset_data`, `ccu_reset_controller_data`, `ccu_reset_controller`, `RESET_DATA()`, and the common `spacemit_reset_probe()` prototype. The data model encodes one reset as register offset plus assert/deassert masks.

Control flow: no direct runtime flow, but SoC drivers use `RESET_DATA()` to build tables consumed by the common probe and ops.

State and persistence: header declares structures used to hold runtime controller state and static reset tables; no independent state.

Dependencies and integration: includes auxiliary bus, regmap, reset-controller, and integer types. It is the compile-time link between K1/K3 table files and common implementation.

Risks and test signals: mask semantics are flexible but easy to misencode when hardware uses clear-to-deassert or separate bits. Compile tests catch signature drift; hardware tests validate each table entry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/spacemit/reset-spacemit-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/spacemit/reset-spacemit-k1.c -->
# sources/distributed-fs/ceph-client/drivers/reset/spacemit/reset-spacemit-k1.c

Purpose: SpacemiT K1 reset table driver exposing MPMU, APBC, APMU, RCPU, RCPU2, and APBC2 reset domains through common CCU reset code.

Important APIs/types/functions: static `ccu_reset_data` arrays encode K1 reset IDs from SpacemiT clock/syscon bindings into register offsets and masks. `K1_AUX_DEV_ID()` builds auxiliary device IDs whose `driver_data` points at domain-specific `ccu_reset_controller_data`. The auxiliary driver uses `spacemit_reset_probe()`.

Control flow: K1 CCU creates matching auxiliary devices; each device registers one reset controller for its domain. Runtime ops are delegated to common regmap mask updates.

State and persistence: tables are static; parent CCU register bits hold reset state. No additional mutable state in this file.

Dependencies and integration: SpacemiT K1 syscon/clock bindings, auxiliary bus, common SpacemiT reset namespace, and parent CCU regmap.

Risks and test signals: table entries with identical offsets and masks for multiple PWM resets may reflect shared hardware but need binding validation. Test all auxiliary IDs, binding/table count alignment, register mask polarity, and module namespace import.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/spacemit/reset-spacemit-k1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/spacemit/reset-spacemit-k3.c -->
# sources/distributed-fs/ceph-client/drivers/reset/spacemit/reset-spacemit-k3.c

Purpose: SpacemiT K3 reset table driver for MPMU, APBC, APMU, and DCIU domains using the common CCU reset implementation.

Important APIs/types/functions: K3 domain arrays map `spacemit,k3-resets.h` reset IDs to syscon register offsets and assert/deassert masks. `K3_AUX_DEV_ID()` creates auxiliary IDs named `spacemit_ccu.k3-*-reset`; each carries a `ccu_reset_controller_data` pointer. The auxiliary driver probes through `spacemit_reset_probe()`.

Control flow: parent K3 CCU auxiliary devices instantiate per-domain reset controllers. Assert/deassert behavior is common regmap mask writing.

State and persistence: hardware CCU bits persist reset state; software only provides static tables and auxiliary driver registration.

Dependencies and integration: K3 syscon headers, reset dt-bindings, auxiliary bus, common SpacemiT reset code, and parent CCU.

Risks and test signals: the large APMU table is binding-sensitive; sparse or duplicated IDs would expose wrong masks. Test each domain auxiliary device, table count vs binding end values, CPU/UCIE/PCIe reset polarity, and all build modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/spacemit/reset-spacemit-k3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/starfive/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/reset/starfive/Kconfig

Purpose: Kconfig definitions for StarFive JH71x0 common reset support and JH7100/JH7110 SoC drivers.

Important APIs/types/functions: `RESET_STARFIVE_JH71X0` is hidden common code. `RESET_STARFIVE_JH7100` depends on `ARCH_STARFIVE || COMPILE_TEST`; `RESET_STARFIVE_JH7110` depends on `CLK_STARFIVE_JH7110_SYS`, selects `AUXILIARY_BUS`, and both select common JH71x0 support.

Control flow: build-time only. Defaults follow `ARCH_STARFIVE`, producing built-in bool drivers.

State and persistence: generated kernel config selects which reset providers are compiled.

Dependencies and integration: ties reset support to StarFive architecture or clock-controller providers.

Risks and test signals: JH7110 reset devices require the clock driver to publish auxiliary devices. Test dependency-disabled configs, COMPILE_TEST, and JH7100/JH7110 independent selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/starfive/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/starfive/Makefile -->
# sources/distributed-fs/ceph-client/drivers/reset/starfive/Makefile

Purpose: Kbuild object selection for StarFive reset drivers.

Important APIs/types/functions: common `reset-starfive-jh71x0.o` is built for `CONFIG_RESET_STARFIVE_JH71X0`; SoC front-ends build `reset-starfive-jh7100.o` and `reset-starfive-jh7110.o`.

Control flow: no runtime behavior; Kbuild assembles common and SoC-specific objects based on config.

State and persistence: build graph state only.

Dependencies and integration: common object exports `reset_starfive_jh71x0_register()` used by both SoC drivers.

Risks and test signals: object selection must stay aligned with Kconfig selects or SoC drivers will miss common symbols. Test JH7100-only and JH7110-only builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/starfive/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/starfive/reset-starfive-jh7100.c -->
# sources/distributed-fs/ceph-client/drivers/reset/starfive/reset-starfive-jh7100.c

Purpose: StarFive JH7100 reset provider front-end that maps reset assert/status registers and uses the common JH71x0 reset implementation.

Important APIs/types/functions: register offsets define four assert and four status banks. `jh7100_reset_asserted[]` records status bits whose asserted polarity is not inverted. `jh7100_reset_probe()` maps MMIO and calls `reset_starfive_jh71x0_register()` with assert base, status base, asserted-status table, and `JH7100_RSTN_END`.

Control flow: built-in platform probe binds `starfive,jh7100-reset`, registers the common controller, and suppresses bind attributes.

State and persistence: hardware registers store reset state; static status-polarity array captures SoC quirks.

Dependencies and integration: platform MMIO, JH7100 reset dt-bindings, common StarFive reset helper, reset framework.

Risks and test signals: status polarity table must match hardware exactly or polling can time out. Test all banks, status inversion exceptions, reset pulse operation, and resource mapping failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/starfive/reset-starfive-jh7100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/starfive/reset-starfive-jh7110.c -->
# sources/distributed-fs/ceph-client/drivers/reset/starfive/reset-starfive-jh7110.c

Purpose: StarFive JH7110 auxiliary reset front-end for sys, aon, stg, isp, and vout reset domains.

Important APIs/types/functions: `jh7110_reset_info` provides per-domain reset count and assert/status offsets. `jh7110_reset_probe()` converts the auxiliary device to `jh71x0_reset_adev`, validates base/info, and calls `reset_starfive_jh71x0_register()`.

Control flow: JH7110 clock/sys controller creates auxiliary devices named `clk_starfive_jh7110_sys.rst-*`; each binds to one reset domain and registers common JH71x0 ops.

State and persistence: domain info tables are static; hardware registers hold state.

Dependencies and integration: auxiliary bus, StarFive clock driver auxiliary data, common JH71x0 reset helper, JH7110 dt-bindings.

Risks and test signals: OF node passed from parent, so child device-tree matching depends on clock-controller topology. Test all five auxiliary IDs, reset counts, offset correctness, and parent base absence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/starfive/reset-starfive-jh7110.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/starfive/reset-starfive-jh71x0.c -->
# sources/distributed-fs/ceph-client/drivers/reset/starfive/reset-starfive-jh71x0.c

Purpose: common StarFive JH71x0 reset controller implementation for assert/status register banks with optional custom asserted-status polarity.

Important APIs/types/functions: `jh71x0_reset` stores rcdev, spinlock, assert/status bases, and optional asserted table. `jh71x0_reset_update()` RMWs assert bits and polls the status bit with `readl_poll_timeout_atomic()`. `.reset` asserts then deasserts. `reset_starfive_jh71x0_register()` exports common registration.

Control flow: SoC front-ends call the export with register bases and reset count. Runtime assert/deassert holds a spinlock around RMW and status polling.

State and persistence: register bits hold reset state; software tracks bases and status polarity. Device-managed registration owns lifetime.

Dependencies and integration: MMIO accessors, atomic polling, spinlocks, reset framework, exported symbol for SoC drivers.

Risks and test signals: polling while the associated clock is gated can time out; code comments identify this risk. Test timeout behavior, concurrent reset operations, asserted-table and default polarity, and reset pulse sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/starfive/reset-starfive-jh71x0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/starfive/reset-starfive-jh71x0.h -->
# sources/distributed-fs/ceph-client/drivers/reset/starfive/reset-starfive-jh71x0.h

Purpose: local header declaring the common StarFive JH71x0 reset registration helper.

Important APIs/types/functions: `reset_starfive_jh71x0_register()` takes device, OF node, assert/status MMIO bases, optional asserted-status table, reset count, and owner module pointer.

Control flow: no runtime flow; JH7100 and JH7110 front-ends include this header and call the helper from probe.

State and persistence: no state in the header.

Dependencies and integration: relies on declarations of `struct device`, `struct device_node`, and `struct module` from including C files; links SoC front-ends to common implementation.

Risks and test signals: signature drift breaks both front-ends at compile time. Compile coverage for both SoC drivers is the main signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/starfive/reset-starfive-jh71x0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/sti/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/reset/sti/Kconfig

Purpose: Kconfig gate for STiH407 reset driver support.

Important APIs/types/functions: `STIH407_RESET` is a bool visible under `COMPILE_TEST` and enabled only within `ARCH_STI || COMPILE_TEST`.

Control flow: build-time only; selects whether STiH407 reset objects are compiled.

State and persistence: generated kernel config is the only state.

Dependencies and integration: scoped to STi architecture or compile testing; object mapping is in the adjacent Makefile.

Risks and test signals: no explicit dependency on syscon/regmap because those are generally available subsystems; build tests under COMPILE_TEST catch missing includes or symbol drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/sti/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/sti/Makefile -->
# sources/distributed-fs/ceph-client/drivers/reset/sti/Makefile

Purpose: Kbuild mapping for STi reset support.

Important APIs/types/functions: `obj-$(CONFIG_STIH407_RESET) += reset-stih407.o reset-syscfg.o` builds the SoC data file and generic syscfg reset implementation together.

Control flow: no runtime behavior; build-time object selection only.

State and persistence: no runtime state.

Dependencies and integration: ensures `reset-stih407.c` has the `syscfg_reset_probe()` implementation available from `reset-syscfg.c`.

Risks and test signals: omitting either object causes unresolved symbols or no device data. Test with `CONFIG_STIH407_RESET=y` and disabled configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/sti/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/sti/reset-stih407.c -->
# sources/distributed-fs/ceph-client/drivers/reset/sti/reset-stih407.c

Purpose: STiH407 reset data provider, defining powerdown, softreset, and picophy reset channels and registering them through the generic syscfg reset code.

Important APIs/types/functions: macros such as `STIH407_PDN_*` and `STIH407_SRST_*` build `syscfg_reset_channel_data` entries. Three `syscfg_reset_controller_data` instances describe acked powerdowns, active-low softresets, and picophy resets. Platform driver probe is `syscfg_reset_probe()`.

Control flow: arch init registers the platform driver early. OF match data selects a controller data block, and `reset-syscfg.c` performs actual regmap field registration and operations.

State and persistence: this file has only static channel tables; hardware syscfg registers hold reset/powerdown state.

Dependencies and integration: STiH407 reset dt-bindings, syscon compatible strings for core/SBC/LPM registers, generic syscfg reset implementation.

Risks and test signals: channel indices must match binding IDs. Powerdown entries wait for ack while softreset entries do not. Test all compatibles, ack timeout paths, active-low softreset polarity, and syscon compatible lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/sti/reset-stih407.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/sti/reset-syscfg.c -->
# sources/distributed-fs/ceph-client/drivers/reset/sti/reset-syscfg.c

Purpose: generic ST syscfg reset-controller implementation using regmap fields for reset and optional acknowledge bits.

Important APIs/types/functions: `syscfg_reset_channel` stores reset/ack fields; `syscfg_reset_controller` embeds rcdev plus flexible channel array. `syscfg_reset_program_hw()` writes reset polarity and optionally polls ack. `syscfg_reset_status()` reads ack or reset field. `syscfg_reset_controller_register()` allocates fields from syscon regmaps and registers the controller.

Control flow: SoC data probe passes a `syscfg_reset_controller_data` through match data. Registration resolves each channel’s syscon compatible, builds fields, then exposes reset ops.

State and persistence: software stores regmap-field handles; hardware syscfg bits hold reset state. Allocation is devm, but `reset_controller_register()` is not devm-wrapped in this file.

Dependencies and integration: regmap fields, syscon lookup by compatible, platform OF match data, reset framework.

Risks and test signals: no explicit unregister path because driver is arch-init/built-in style. Ack polling timeout is one second. Test bad compatible strings, active-low behavior, ack and no-ack controllers, invalid IDs, and timeout handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/sti/reset-syscfg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/sti/reset-syscfg.h -->
# sources/distributed-fs/ceph-client/drivers/reset/sti/reset-syscfg.h

Purpose: shared declarations and macros for ST syscfg reset channel descriptions.

Important APIs/types/functions: `syscfg_reset_channel_data` describes syscon compatible plus reset/ack reg fields. `_SYSCFG_RST_CH()` and `_SYSCFG_RST_CH_NO_ACK()` build entries. `syscfg_reset_controller_data` configures ack waiting, active-low polarity, channel count, and channel array. Declares `syscfg_reset_probe()`.

Control flow: no runtime flow, but macro-generated tables drive `reset-syscfg.c`.

State and persistence: no independent state; structures become static SoC data.

Dependencies and integration: device, regmap, reset-controller headers; used by `reset-stih407.c` and generic syscfg implementation.

Risks and test signals: macro arguments are raw offsets/bits, so binding mistakes compile cleanly. Compile tests plus hardware reset/ack validation are required.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/sti/reset-syscfg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/tegra/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/reset/tegra/Kconfig

Purpose: Kconfig option for NVIDIA Tegra BPMP reset support.

Important APIs/types/functions: `RESET_TEGRA_BPMP` is a bool visible under COMPILE_TEST and defaults to `TEGRA_BPMP`.

Control flow: build-time selection only; runtime initialization is called by the BPMP driver.

State and persistence: kernel config controls inclusion.

Dependencies and integration: relies on Tegra BPMP support to provide reset IDs and message transport.

Risks and test signals: if defaulting diverges from BPMP availability, reset support may be compiled without usable firmware. Test COMPILE_TEST and Tegra BPMP enabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/tegra/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/tegra/Makefile -->
# sources/distributed-fs/ceph-client/drivers/reset/tegra/Makefile

Purpose: Kbuild mapping for Tegra BPMP reset support.

Important APIs/types/functions: builds `reset-bpmp.o` when `CONFIG_RESET_TEGRA_BPMP` is enabled.

Control flow: build-time only.

State and persistence: no runtime state.

Dependencies and integration: object provides `tegra_bpmp_init_resets()` for the BPMP core.

Risks and test signals: missing object breaks BPMP reset registration. Compile with BPMP enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/tegra/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/tegra/reset-bpmp.c -->
# sources/distributed-fs/ceph-client/drivers/reset/tegra/reset-bpmp.c

Purpose: Tegra BPMP reset-controller implementation that forwards reset requests to BPMP firmware using MRQ_RESET messages.

Important APIs/types/functions: `tegra_bpmp_reset_common()` builds `mrq_reset_request` and `tegra_bpmp_message`, calls `tegra_bpmp_transfer()`, and maps BPMP return values. `.reset`, `.assert`, and `.deassert` wrap BPMP commands. `tegra_bpmp_init_resets()` fills the embedded `bpmp->rstc` and registers it.

Control flow: BPMP core initializes reset support after it knows `soc->num_resets`. Consumers call reset ops, which synchronously send firmware messages.

State and persistence: controller is embedded in `struct tegra_bpmp`; firmware owns hardware reset state.

Dependencies and integration: Tegra BPMP core, BPMP ABI, reset-controller framework.

Risks and test signals: any nonzero BPMP message return becomes `-EINVAL`, losing detailed firmware errors. Test firmware transfer failures, invalid reset IDs, all three commands, and `num_resets` correctness for each SoC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/tegra/reset-bpmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rpmsg/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/rpmsg/Kconfig

Purpose: Kconfig menu for RPMsg core, user interfaces, name service, MediaTek SCP, Qualcomm GLINK/SMD, and Virtio RPMsg transports.

Important APIs/types/functions: key symbols include `RPMSG`, `RPMSG_CHAR`, `RPMSG_CTRL`, `RPMSG_NS`, `RPMSG_MTK_SCP`, `RPMSG_QCOM_GLINK`, `RPMSG_QCOM_GLINK_RPM`, `RPMSG_QCOM_GLINK_SMEM`, `RPMSG_QCOM_SMD`, and `RPMSG_VIRTIO`. Dependencies select transport prerequisites such as NET, MTK_SCP, MAILBOX, QCOM_SMEM, VIRTIO, and RPMSG_NS.

Control flow: build-time feature selection only; transport and bus behavior lives in C files.

State and persistence: generated kernel config controls which RPMsg modules are built.

Dependencies and integration: hides `RPMSG` as a selected core and exposes transport/user API options to platform configs.

Risks and test signals: dependency changes can silently drop user APIs or transports. Test allmodconfig, minimal RPMSG transport configs, `RPMSG_CTRL` with and without `RPMSG_CHAR`, and Qualcomm/virtio dependency matrices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rpmsg/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rpmsg/Makefile -->
# sources/distributed-fs/ceph-client/drivers/rpmsg/Makefile

Purpose: Kbuild object map for RPMsg core, character/control/name-service helpers, and platform transports.

Important APIs/types/functions: builds core files based on `CONFIG_RPMSG*`. `qcom_glink-objs` composes `qcom_glink_native.o` and `qcom_glink_ssr.o`; `CFLAGS_qcom_glink_native.o := -I$(src)` lets trace/header includes resolve locally.

Control flow: no runtime flow; Kbuild links transport modules from selected objects.

State and persistence: build graph only.

Dependencies and integration: maps Kconfig symbols to the RPMsg bus implementation, MediaTek SCP, Qualcomm GLINK/SMD, and Virtio transport objects.

Risks and test signals: composite object drift can omit native or SSR pieces. Test modular and built-in builds for each transport and trace include generation for `qcom_glink_native.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rpmsg/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rpmsg/mtk_rpmsg.c -->
# sources/distributed-fs/ceph-client/drivers/rpmsg/mtk_rpmsg.c

Purpose: MediaTek SCP RPMsg bridge that uses SCP IPI channels to create RPMsg devices and endpoints, including name-service handling.

Important APIs/types/functions: `mtk_rpmsg_rproc_subdev` tracks the platform device, transport callbacks, NS endpoint, work item, and channel list. `__mtk_create_ept()` registers an IPI handler and builds an endpoint. `mtk_rpmsg_ns_cb()` creates channels from name-service messages. `mtk_rpmsg_create_rproc_subdev()` exports a remoteproc subdevice with prepare/stop/unprepare hooks.

Control flow: remoteproc prepare creates the NS endpoint if configured. Incoming NS IPI messages enqueue channel info and schedule work to register rpmsg devices. Stop destroys the NS endpoint, cancels registration work, unregisters devices, and frees channel records.

State and persistence: channel list tracks discovered services and registered status for the remoteproc lifetime. Endpoints are kref-counted and freed on destroy.

Dependencies and integration: remoteproc subdevices, MediaTek SCP IPI callbacks from `mtk_rpmsg_info`, RPMsg core, OF child matching by `mediatek,rpmsg-name`, and workqueues.

Risks and test signals: duplicate NS announcements are not deduplicated before list insertion. `trysend` is currently blocking-equivalent. Test malformed NS messages, remoteproc crash/stop cleanup, duplicate service announcements, endpoint destroy/unregister paths, and OF subnode matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rpmsg/mtk_rpmsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rpmsg/qcom_glink_native.c -->
# sources/distributed-fs/ceph-client/drivers/rpmsg/qcom_glink_native.c

Purpose: core Qualcomm GLINK native RPMsg transport implementation, handling version negotiation, channel open/close, intent-based and intentless data transfer, flow control, RPMsg device creation, and teardown.

Important APIs/types/functions: `qcom_glink` owns RX/TX pipes, work queues, IDRs for local/remote channel IDs, feature flags, and TX abort state. `glink_channel` owns an RPMsg endpoint, local/remote IDs, intent IDRs, completions, receive callback lock, and intent request state. Key functions include `qcom_glink_tx()`, `qcom_glink_native_rx()`, `qcom_glink_work()`, `qcom_glink_rx_data()`, `qcom_glink_rx_open()/close()`, `__qcom_glink_send()`, `qcom_glink_create_ept()`, `qcom_glink_native_probe()`, and `qcom_glink_native_remove()`.

Control flow: probe initializes locks/IDRs/work, reads the edge label, adds sysfs groups, sends version negotiation, and creates the rpmsg control device. RX interrupt callers invoke `qcom_glink_native_rx()`, which handles simple data/status commands inline and defers channel-control commands to workqueue context. Local or remote opens perform a two-sided open/open-ack handshake before endpoints become usable. Transmit selects a remote intent or requests one, chunks large payloads, writes GLINK data headers/payloads to the TX pipe, and kicks the transport. Removal cancels RX work, aborts writers, unregisters child devices, releases channels, and destroys IDRs.

State and persistence: all state is in-memory per edge and per channel. IDRs persist channel/intent mappings until close or remove. Reusable intents stay advertised; non-reuse intents are freed after RX_DONE. Hardware/shared-memory pipe state is owned by the transport-specific pipe provider.

Dependencies and integration: RPMsg core and ctrl-dev, GLINK SSR companion object, transport-specific `qcom_glink_pipe` providers, workqueues, wait queues, completions, IDR, tracepoints, OF child matching by `qcom,glink-channels`, and optional intentless operation.

Risks and test signals: concurrency is high risk: RX, deferred work, endpoint destroy, close-ack, and remove all mutate channel state. `qcom_glink_cancel_rx_work()` frees queued commands without `list_del`, acceptable only because the queue is discarded after cancellation. Timeout paths in open and intent request must release the right references. Test version negotiation, local and remote open races, close during send, remove while TX waits, intent request timeout/denial, fragmented messages, intentless mode, flow-control callback delivery, and lockdep/KASAN under SSR restarts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rpmsg/qcom_glink_native.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rpmsg/qcom_glink_native.h -->
# sources/distributed-fs/ceph-client/drivers/rpmsg/qcom_glink_native.h

Purpose: public internal interface between Qualcomm GLINK native core and concrete GLINK pipe transports.

Important APIs/types/functions: feature bits include `GLINK_FEATURE_INTENT_REUSE`, `GLINK_FEATURE_MIGRATION`, and `GLINK_FEATURE_TRACER_PKT`. `struct qcom_glink_pipe` abstracts FIFO length and callbacks for availability, peek, advance, write, and kick. Exports `qcom_glink_native_probe()`, `qcom_glink_native_remove()`, and `qcom_glink_native_rx()`.

Control flow: transport drivers provide RX/TX pipe implementations and call probe to create a GLINK edge, call RX when data arrives, and call remove during teardown.

State and persistence: header declares opaque `struct qcom_glink`; actual state is private to `qcom_glink_native.c`.

Dependencies and integration: uses Linux types and device forward declarations; consumed by GLINK SMEM/RPM-style transports.

Risks and test signals: pipe callback contracts are critical; wrong `avail`, alignment, or `advance` behavior corrupts protocol parsing. Test with each pipe backend, RX/TX wraparound, zero/large messages, and teardown ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rpmsg/qcom_glink_native.h -->
