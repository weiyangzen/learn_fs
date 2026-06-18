# subset-b-001069 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/fsl-mc/fsl-mc-bus.c -->
# sources/distributed-fs/ceph-client/drivers/bus/fsl-mc/fsl-mc-bus.c

Purpose: implements the Freescale/NXP Management Complex platform and `fsl-mc` bus core. It registers the `fsl-mc` bus type, binds MC object drivers by vendor/type, creates Linux devices for DPRC and child objects, configures DMA/IOMMU identity through ICIDs, exposes `rescan` and `autorescan` bus attributes, and probes the root `fsl,qoriq-mc`/`NXP0008` platform device.

Important APIs and types: `struct fsl_mc` stores the root DPRC, address translation ranges, and MC control registers. `struct fsl_mc_addr_translation_range` maps MC offsets to CPU physical addresses. Exported entry points include `fsl_mc_bus_type`, device types for object classes, `__fsl_mc_driver_register()`, `fsl_mc_driver_unregister()`, `fsl_mc_get_version()`, `fsl_mc_device_add()`, `fsl_mc_device_remove()`, and `fsl_mc_get_endpoint()`.

Control flow: `postcore_initcall()` registers the bus, platform driver, DPRC driver, allocator driver, and a platform-bus notifier. Probe maps optional MC registers, resumes firmware after IOMMU setup, creates root MC I/O, queries firmware version/container ID/API version, parses DT ranges, and adds the root DPRC device. Device addition allocates either `struct fsl_mc_bus` for DPRCs or `struct fsl_mc_device`, fills object descriptors, ICIDs, DMA masks, MSI domains, MMIO regions, and calls `device_add()`.

State and persistence: state is runtime-only: global firmware version, global portal base workaround, per-platform root bus data, bus scan mutexes, and device-model objects. Remove destroys root MC I/O, unregisters notifier, and pauses MC firmware to make kexec safer.

Dependencies and integration: depends on DPRC firmware commands, `mc_send_command()`, FSL MC allocator/IRQ helpers, OF/ACPI DMA configuration, IOMMU default-domain APIs, MSI domains, and Linux device model matching/modalias. Integration points are sysfs bus controls, platform probe/remove, DPRC object scanning, and exported registration helpers for MC client drivers.

Risks: address translation and the DPMCP base-address workaround are firmware-version sensitive; DMA configuration depends on the correct root ancestor and ICID; `autorescan_show()` assumes a root DPRC writes the buffer; notifier/probe ordering matters because MC firmware may fault if not paused before SMMU setup. Test signals include OF and ACPI probe, root DPRC enumeration, `rescan`, `autorescan`, child DPRC endpoint lookup, IOMMU domain attach/detach, MSI inheritance, and kexec/remove behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/fsl-mc/fsl-mc-bus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/fsl-mc/fsl-mc-msi.c -->
# sources/distributed-fs/ceph-client/drivers/bus/fsl-mc/fsl-mc-msi.c

Purpose: provides MSI domain glue for `fsl-mc` devices. It creates FSL MC MSI IRQ domains, finds the right firmware-described domain for child objects, allocates/free MSI descriptors, and programs MSI address/data pairs into MC objects through DPRC commands.

Important APIs: `fsl_mc_msi_create_irq_domain()` adjusts MSI domain/chip callbacks and tags the domain as `DOMAIN_BUS_FSL_MC_MSI`; `fsl_mc_find_msi_domain()` maps OF `msi-map` or ACPI IORT domains using the device ICID; `fsl_mc_msi_domain_alloc_irqs()` and `fsl_mc_msi_domain_free_irqs()` wrap generic MSI allocation. Internally, `fsl_mc_domain_calc_hwirq()` combines ICID and MSI index, and `fsl_mc_msi_write_msg()` programs hardware.

Control flow: on domain creation, default ops are filled when requested: `set_desc` computes readable unique hwirqs, and `irq_write_msi_msg` stores the MSI message then calls `dprc_set_irq()` for a DPRC IRQ or `dprc_set_obj_irq()` for child-object IRQs. Allocation initializes device MSI data and allocates the requested range.

State and persistence: no persistent storage; state lives in generic MSI descriptors and the owning bus IRQ resource table. The MC firmware persists the programmed IRQ target until reprogrammed or object reset. Freeing with a zero MSI address is intentionally ignored because the MC does not require explicit unprogramming.

Dependencies and integration: depends on generic MSI domains, irqdomain, OF MSI mapping, ACPI IORT, FSL MC bus ICID/root traversal, and DPRC IRQ command wrappers. It integrates with `fsl_mc_device_add()` via inherited MSI domains and with MC allocator-provided `irq_resources`.

Risks: wrong owner-device association in `irq_resources` programs the wrong MC object; ICID-based hwirq construction must remain unique within the domain; level-capable domains are force-cleared; missing OF `msi-map` falls back to parent domain, which is intentional but platform-sensitive. Test signals are MSI allocation/free, interrupt delivery for DPRC and child objects, OF fallback behavior, ACPI IORT domain lookup, and error paths from `dprc_set_irq()`/`dprc_set_obj_irq()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/fsl-mc/fsl-mc-msi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/fsl-mc/fsl-mc-private.h -->
# sources/distributed-fs/ceph-client/drivers/bus/fsl-mc/fsl-mc-private.h

Purpose: central private contract for the FSL MC bus implementation. It defines MC firmware command IDs, packed command/response structures, minimum supported object API versions, DPRC/DPBP/DPCON/generic object command interfaces, resource-pool bookkeeping, UAPI state, and internal helper prototypes shared by bus, IRQ, allocator, DPRC, portal, and UAPI code.

Important types and APIs: command structs include DPMNG version response, DPMCP open/close/reset, DPRC IRQ/config/object/region/connection messages, DPBP/DPCON attributes, and generic object open/reset. `struct fsl_mc_resource_pool` owns typed free lists with a mutex. `struct fsl_mc_uapi` tracks the miscdevice and shared static portal use. `struct fsl_mc_bus` embeds the DPRC `fsl_mc_device`, resource pools, IRQ resources, scan mutex, DPRC attributes, UAPI object, and IRQ enabled state.

Control flow role: this header is not executable but defines the ABI used by command builders in `mc-sys.c`, DPRC code, `obj-api.c`, and `fsl-mc-bus.c`. The command IDs encode firmware API versions and command numbers; consumers fill command structures, call `mc_send_command()`, then decode little-endian responses.

State and persistence: declares in-memory resource pools, UAPI portal-use state, and per-bus scan/IRQ state. It does not persist data across boots; MC firmware is the authoritative source for object/container attributes.

Dependencies and integration: depends on public `<linux/fsl/mc.h>`, mutex/list/device model, miscdevice/ioctl support, and all FSL MC subsystem compilation units. Its fallback inline UAPI functions make `CONFIG_FSL_MC_UAPI_SUPPORT` optional without changing bus probe behavior.

Risks: command layout must match firmware exactly, including endian and padding; version constants gate portal/object support; structs shared between files can create subtle ABI drift if changed without command encoders/decoders. Test signals include building with and without UAPI, DPRC object scan, IRQ allocation, resource pool allocation/free, generic object open/close/reset, and compatibility against supported MC firmware versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/fsl-mc/fsl-mc-private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/fsl-mc/fsl-mc-uapi.c -->
# sources/distributed-fs/ceph-client/drivers/bus/fsl-mc/fsl-mc-uapi.c

Purpose: exposes a controlled userspace miscdevice for sending selected Management Complex commands to the root DPRC. It allows management tooling to query or modify MC resources while filtering the command set and requiring `CAP_NET_ADMIN` for resource-changing operations.

Important APIs and types: `struct uapi_priv_data` binds an open file to a `fsl_mc_uapi` and an MC portal. `struct fsl_mc_cmd_desc` describes accepted command IDs, masks, payload sizes, token expectations, and security flags. Public internal entry points are `fsl_mc_uapi_create_device_file()` and `fsl_mc_uapi_remove_device_file()`.

Control flow: miscdevice open serializes access to a static root portal for the first opener, otherwise allocates a dynamic DPMCP portal. `FSL_MC_SEND_MC_COMMAND` copies a full `struct fsl_mc_command` from userspace, calls `fsl_mc_command_check()`, sends it through `mc_send_command()`, and copies the response back. Release returns dynamic portals or clears the static-in-use flag.

State and persistence: per-open state is heap allocated and released on close. The shared `local_instance_in_use` flag protects the static portal. No persistent state is written, but accepted commands can change MC firmware object state.

Dependencies and integration: depends on FSL MC command header decoding, portal allocation, miscdevice, copy_from/to_user, Linux capabilities, and root `fsl_mc_bus` lifetime. It integrates with `fsl_mc_bus` only when UAPI support is enabled.

Risks: the allowlist is the primary security boundary. Size checks require all unused bytes past a command's declared size to be zero, token presence must match the command, and generic CREATE/DESTROY/OPEN/API_VERSION commands validate module IDs. Incorrect allowlist sizes or masks could permit malformed firmware commands; dynamic portal allocation failures limit concurrent opens. Test signals include accepted/rejected command IDs, garbage tail rejection, token mismatch rejection, CAP_NET_ADMIN gating, concurrent opens, portal release, and ioctl copy fault handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/fsl-mc/fsl-mc-uapi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/fsl-mc/mc-io.c -->
# sources/distributed-fs/ceph-client/drivers/bus/fsl-mc/mc-io.c

Purpose: manages MC portal I/O objects. It maps portal MMIO, associates portals with DPMCP objects, allocates portals from MC bus resource pools, and releases them back to the pool.

Important APIs: `fsl_create_mc_io()` creates an `fsl_mc_io` with either mutex or raw spinlock serialization depending on `FSL_MC_IO_ATOMIC_CONTEXT_PORTAL`; `fsl_destroy_mc_io()` unmaps and releases the portal; `fsl_mc_portal_allocate()` allocates a DPMCP resource and wraps its MMIO region; `fsl_mc_portal_free()` destroys the wrapper and returns the resource. Internal helpers open/close DPMCPs and bind `dpmcp_dev->mc_io`.

Control flow: creation allocates managed memory, requests the portal memory region, maps it, initializes locking, and optionally opens a DPMCP. Portal allocation resolves the owning DPRC, allocates a DPMCP resource, validates its minimum API version, creates an MC I/O object on the DPMCP region, and adds a device link from consumer to DPMCP except when the DPRC consumes its own portal for UAPI.

State and persistence: state is in `struct fsl_mc_io`, DPMCP device handle fields, resource ownership, and optional device links. Nothing persists outside kernel runtime; the firmware DPMCP open handle is closed on destruction.

Dependencies and integration: depends on FSL MC resource pools, DPMCP open/close commands, devm memory-region/ioremap helpers, device links, and public MC command sending. It is used by root bus probe, UAPI open, MC object drivers, and allocator users.

Risks: portal ownership must be exclusive; double assignment is rejected by checking both `mc_io->dpmcp_dev` and `dpmcp_dev->mc_io`. DPMCP version mismatches fail allocation. Early returns in `fsl_mc_portal_free()` can leak a malformed resource state if invariants are already broken. Test signals include root portal creation, dynamic portal allocation/free, DPMCP open/close failures, device-link creation, atomic-context portal use, and resource pool accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/fsl-mc/mc-io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/fsl-mc/mc-sys.c -->
# sources/distributed-fs/ceph-client/drivers/bus/fsl-mc/mc-sys.c

Purpose: low-level command transport for FSL MC portals. It writes command parameters/header to portal MMIO, polls for firmware completion, reads responses, maps MC firmware statuses to Linux errors, and serializes each portal.

Important APIs: exported `mc_send_command()` is the main entry point. `mc_cmd_hdr_read_cmdid()` exposes command ID decoding. Internal helpers read status, translate status/error strings, perform endian-aware `writeq`/`readq` portal access, and implement preemptible versus atomic polling.

Control flow: callers fill `struct fsl_mc_command`. `mc_send_command()` rejects hardirq use on non-atomic portals, locks the portal, writes params first and header last, then polls until status is no longer READY or timeout. Non-atomic portals use `usleep_range()`; atomic portals use `udelay()` under raw spinlock. On OK status, response params are copied into the command. On error, MC status maps to errno.

State and persistence: state is limited to the caller's command buffer and portal lock. MC firmware state changes happen as side effects of commands; this file does not retain them.

Dependencies and integration: depends on `struct fsl_mc_io` locking mode, MMIO helpers, command header layout from public/private MC headers, jiffies timing, and kernel errno conventions. It underpins bus probe, DPRC scans, MSI programming, object APIs, and UAPI.

Risks: command completion timeout is 15 seconds; atomic portals busy-wait for the whole timeout budget. Endian handling intentionally compensates for IO accessors, so changing it is high risk. Missing command completion interrupts are noted as a TODO. Test signals include successful/failed MC commands, status-to-errno mapping, timeout path, hardirq rejection for sleeping portals, concurrent command serialization, and response endian correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/fsl-mc/mc-sys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/fsl-mc/obj-api.c -->
# sources/distributed-fs/ceph-client/drivers/bus/fsl-mc/obj-api.c

Purpose: provides generic open, close, and reset wrappers for FSL MC object types. It lets drivers operate on many MC object classes without embedding object-specific command IDs in each caller.

Important APIs: `fsl_mc_obj_open()` maps an object type string such as `dpni`, `dpio`, `dpmcp`, or `dpdmai` to its open command ID, sends the open command, and returns the firmware token. `fsl_mc_obj_close()` sends generic close with a token. `fsl_mc_obj_reset()` sends generic reset with a token.

Control flow: `fsl_mc_get_open_cmd_id()` searches a static type-to-command table. Open encodes the selected command ID with no token, stores the object ID in little-endian command params, calls `mc_send_command()`, and reads the returned token from the header. Close/reset encode generic command IDs with the supplied token and send them.

State and persistence: no local persistent state. The returned token represents a firmware-side open object handle and remains valid until close/reset semantics are invoked by callers.

Dependencies and integration: depends on command IDs and `struct fsl_mc_obj_cmd_open` from `fsl-mc-private.h`, public command header helpers, and `mc_send_command()`. It is exported for MC client drivers and management paths that need generic object control.

Risks: type strings must match firmware object descriptors exactly; unknown types return `-ENODEV`. A leaked token means an object may stay open in MC firmware. Test signals include open/close/reset across every listed object type, unknown-type failure, token extraction, and MC status/error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/fsl-mc/obj-api.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/hisi_lpc.c -->
# sources/distributed-fs/ceph-client/drivers/bus/hisi_lpc.c

Purpose: implements the HiSilicon LPC host bridge as an indirect Logical PIO provider, translating Linux I/O port operations into serialized LPC cycles and creating child devices from OF or ACPI firmware descriptions.

Important APIs and types: `struct hisi_lpc_dev` holds the cycle spinlock, MMIO base, and registered `logic_pio_hwaddr`. `hisi_lpc_ops` implements `.in`, `.out`, `.ins`, and `.outs`. ACPI helpers translate child I/O resources, fix known broken firmware resource ranges, and register IPMI or 8250 platform children.

Control flow: probe maps controller registers, registers an indirect PIO range, then either populates OF children or enumerates ACPI children. Each I/O operation translates the logical PIO address to host LPC address, programs operation length/command/address/data FIFO, starts the cycle, polls idle/finished bits, and reads or writes FIFO bytes under `cycle_lock`.

State and persistence: runtime state is the registered PIO range and child platform devices. Hardware register state is programmed per operation; no persistent driver data survives remove. Remove depopulates children and unregisters the PIO range.

Dependencies and integration: depends on `logic_pio`, OF platform population, ACPI resource walking/enumeration, serial8250 platform data, IPMI child matching, MMIO accessors, and spinlock IRQ serialization.

Risks: all LPC cycles are atomic and polling-based; timeout constants assume LPC timing. `outs()` silently stops on write error. ACPI fixups are hard-coded for known firmware defects. Test signals include single and string I/O widths up to four bytes, same-address versus incrementing cycles, timeout/finished error paths, OF child population, ACPI IPMI/UART child creation, resource translation, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/hisi_lpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/imx-aipstz.c -->
# sources/distributed-fs/ceph-client/drivers/bus/imx-aipstz.c

Purpose: configures the i.MX AIPSTZ secure AHB-to-IP bridge, applies SoC default access policy registers, enables runtime PM, and populates simple-bus children underneath the bridge.

Important APIs and types: `struct imx_aipstz_config` holds register defaults for MPR0 and OPACR0-4. `struct imx_aipstz_data` stores the mapped base and selected defaults. `imx_aipstz_apply_default()` writes the policy registers. Runtime resume reapplies the defaults after power-domain loss.

Control flow: probe allocates state, maps the first resource, retrieves match data, writes defaults, stores drvdata, marks runtime PM active, enables runtime PM with devm cleanup, and calls `of_platform_populate()` for `simple-bus` children. Remove depopulates children. Resume calls the same default writer.

State and persistence: policy register state lives in hardware and may be lost on power-off; the driver persists only the mapped base and immutable default config in memory. The imx8mp default sets MPR0 to allow trusted read/write and HPROT-derived privilege for masters 0-7.

Dependencies and integration: depends on OF matching, platform resources, runtime/system PM helpers, and child bus population. It integrates as a parent bus/bridge for devices behind AIPSTZ.

Risks: `devm_platform_get_and_ioremap_resource()` errors are reported as `-ENOMEM` rather than preserving the pointer error, which can hide probe-failure causes. Defaults are SoC-specific and sparse; unsupported OPACR defaults remain zero. Test signals include imx8mp probe, register writes, child device population, runtime suspend/resume restoring registers, system sleep force suspend/resume, and remove depopulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/imx-aipstz.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/imx-weim.c -->
# sources/distributed-fs/ceph-client/drivers/bus/imx-weim.c

Purpose: configures Freescale/NXP i.MX WEIM/EIM external memory bus chip-select timing and creates platform children for devices connected to the external bus. It supports several i.MX variants with different chip-select counts, register counts, strides, and burst clock controls.

Important APIs and types: `struct imx_weim_devtype` describes SoC register layout; `struct cs_timing_state` records timing already applied per chip select to reject conflicts; `weim_timing_setup()` parses `fsl,weim-cs-timing`; `imx_weim_gpr_setup()` programs i.MX50/6 GPR chip-select address layout; dynamic OF notifier creates/destroys children at runtime when enabled.

Control flow: probe maps the WEIM base, enables the clock, and calls `weim_parse_dt()`. Parsing optionally configures GPR ranges, applies burst-clock flags, walks available child nodes, writes timing registers for chip selects referenced in each child `reg`, then populates child platform devices if any timing succeeded.

State and persistence: timing state is cached per chip select to catch contradictory DT overlays. Hardware timing and WCR/GPR bits persist until reset or later writes. Dynamic notifier updates timing and child devices for added/removed nodes.

Dependencies and integration: depends on OF address/range parsing, clocks, syscon/regmap for IOMUXC GPR, OF dynamic reconfiguration, and default platform population. It is a bridge for NOR flash, SRAM, or peripherals on WEIM.

Risks: DT `ranges`, child `reg`, and timing array sizes must match the SoC layout; conflicting timing for shared chip selects fails. Dynamic node add clears fw_devlink's not-device flag before creating children. Test signals include each compatible variant, valid/invalid GPR range encodings, burst-clock options, multiple `reg` entries per child, shared CS conflict detection, OF_DYNAMIC add/remove, and child population failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/imx-weim.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/intel-ixp4xx-eb.c -->
# sources/distributed-fs/ceph-client/drivers/bus/intel-ixp4xx-eb.c

Purpose: configures the Intel IXP4xx external expansion bus chip-select timing registers from device tree, handles SoC-specific quirks for IXP42x/43x/45x/46x, and populates children attached to the expansion bus.

Important APIs and types: `struct ixp4xx_eb` stores regmap, base address, and variant flags. `ixp4xx_exp_tim_props[]` maps DT timing properties to bitfields. `ixp4xx_exp_setup_child()` computes used chip-select sizes from child `reg`; `ixp4xx_exp_setup_chipselect()` reads/modifies/writes CS timing and recurses over adjacent chip selects for large windows.

Control flow: probe gets a syscon regmap from the bus node, reads CNFG0 to determine boot versus normal bus base, logs IXP43x fuse speed, walks children, configures chip selects, then calls `of_platform_default_populate()` if children exist. Each chip select preserves unspecified boot defaults, rounds size to supported powers of two, applies property values with caps, sets cycle type, masks variant-specific bits, and enables the chip select.

State and persistence: hardware CS timing/config registers are modified; no in-memory state beyond probe. Child devices persist in the device model until unbound.

Dependencies and integration: depends on syscon/regmap, OF child parsing, bitfield helpers, and platform population. It integrates with memory-mapped devices behind the legacy expansion bus.

Risks: invalid DT sizes or chip-select indexes are logged but not fatal to the whole probe. Recursive setup for windows larger than one stride assumes contiguous chip-select joining. Some bits are dangerous on certain variants and are deliberately masked or only logged. Test signals include all compatible variants, boot/normal base detection, timing property bounds, large device windows crossing CS boundaries, illegal cycle type, child population, and regmap read/write failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/intel-ixp4xx-eb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/mhi/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/bus/mhi/Kconfig

Purpose: top-level Kconfig include file for the MHI bus subsystem. It does not declare symbols directly; it sources host and endpoint Kconfig files so both halves appear under the MHI bus menu.

Important declarations: it includes `drivers/bus/mhi/host/Kconfig` and `drivers/bus/mhi/ep/Kconfig`.

Control flow and state: configuration-time only. It affects which objects are compiled by making host and endpoint symbols visible to Kconfig.

Dependencies and integration: integrates the MHI host stack (`CONFIG_MHI_BUS`, debugfs, PCI generic controller) and endpoint stack (`CONFIG_MHI_BUS_EP`) into the kernel configuration hierarchy.

Risks and tests: risk is low but path correctness matters; stale source paths would make menuconfig fail. Test signals are `make menuconfig`, `make olddefconfig`, and builds with host-only, endpoint-only, both, and neither enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/mhi/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/mhi/Makefile -->
# sources/distributed-fs/ceph-client/drivers/bus/mhi/Makefile

Purpose: top-level build file for MHI bus host and endpoint subdirectories.

Important declarations: `obj-$(CONFIG_MHI_BUS) += host/` builds the host stack when enabled; `obj-$(CONFIG_MHI_BUS_EP) += ep/` builds the endpoint stack when enabled.

Control flow and state: build-time only; no runtime state. It delegates actual object composition to the subdirectory Makefiles.

Dependencies and integration: links Kconfig symbols to host/endpoint build directories. It assumes subdirectory Makefiles define `mhi.o`, `mhi_ep.o`, and optional controller objects.

Risks and tests: risk is limited to symbol/path drift. Test signals are incremental kernel builds for `CONFIG_MHI_BUS=m/y`, `CONFIG_MHI_BUS_EP=m/y`, and combined host+endpoint configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/mhi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/mhi/common.h -->
# sources/distributed-fs/ceph-client/drivers/bus/mhi/common.h

Purpose: shared MHI protocol register, bitfield, ring-element, context, command, event, and state definitions used by host and endpoint code. It is the local protocol contract for MHI MMIO, BHI/BHIE boot interfaces, command/event TRE encoding, channel/event/command contexts, and state stringification.

Important APIs and types: defines MHI/BHI/BHIE register offsets and masks, TRE helper macros for command, event, data, and RSC descriptors, `enum mhi_pkt_type`, `enum mhi_ev_ccs`, `enum mhi_ch_state`, `enum mhi_cmd_type`, `struct mhi_event_ctxt`, `struct mhi_chan_ctxt`, `struct mhi_cmd_ctxt`, `struct mhi_ring_element`, and inline `mhi_state_str()`.

Control flow role: no executable flow besides the state-string switch, but the macros drive all ring encoding/decoding and context parsing in MHI host and endpoint. Consumers use endian helpers to produce or interpret host-visible descriptors.

State and persistence: describes MMIO registers and host/device shared memory layouts. The structures point to ring base/length/read/write pointers that persist in DMA-coherent shared memory while the controller is active.

Dependencies and integration: depends on `linux/bitfield.h` and public `linux/mhi.h`. It is included by endpoint internals and host boot/debugfs internals.

Risks: bitfield or endian mistakes corrupt cross-host/device protocol state. The RSC pointer macro uses high-bit length packing and must match the MHI spec. Test signals include descriptor round trips, ring context dumps, state string output, host firmware boot, endpoint channel transfers, and sparse/build checks for packed/aligned context fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/mhi/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/mhi/ep/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/bus/mhi/ep/Kconfig

Purpose: declares the endpoint-side MHI bus implementation configuration symbol.

Important declarations: `CONFIG_MHI_BUS_EP` is a tristate named "Modem Host Interface (MHI) bus Endpoint implementation". Help text describes endpoint devices such as SDX55 modem over PCIe.

Control flow and state: configuration-time only. Enabling it selects compilation of the endpoint bus stack through the endpoint Makefile.

Dependencies and integration: no explicit dependency is declared here; controller drivers are expected to provide endpoint transport operations and register with `mhi_ep_register_controller()`.

Risks and tests: risk is that missing dependencies may allow build configurations without required lower-level transport symbols, though the stack itself depends mostly on core kernel facilities. Test signals are `mhi_ep.o` module/builtin builds and endpoint controller driver builds against exported endpoint APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/mhi/ep/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/mhi/ep/Makefile -->
# sources/distributed-fs/ceph-client/drivers/bus/mhi/ep/Makefile

Purpose: builds the endpoint MHI bus stack.

Important declarations: `obj-$(CONFIG_MHI_BUS_EP) += mhi_ep.o`; `mhi_ep-y := main.o mmio.o ring.o sm.o`.

Control flow and state: build-time aggregation only. It links controller registration, MMIO helpers, ring cache/interrupt support, and state-machine helpers into one endpoint object.

Dependencies and integration: driven by `CONFIG_MHI_BUS_EP`; exports symbols consumed by endpoint controller and client drivers.

Risks and tests: path/object drift would drop part of the endpoint stack. Test signals are module and built-in builds, symbol export availability, and link coverage for functions referenced across `main.c`, `mmio.c`, `ring.c`, and `sm.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/mhi/ep/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/mhi/ep/internal.h -->
# sources/distributed-fs/ceph-client/drivers/bus/mhi/ep/internal.h

Purpose: private endpoint-side MHI contract. It offsets generic MHI registers into endpoint BAR space, defines endpoint interrupt/doorbell registers, ring/channel/event state structs, and prototypes shared across endpoint `main`, `mmio`, `ring`, and `sm`.

Important types: `struct mhi_ep_ring` tracks cached host ring context, descriptor cache, offsets, DB registers, event interrupt vector/moderation, and started state. `struct mhi_ep_chan` tracks channel name, paired endpoint device, transfer callback, state, direction, partial TRE state, and lock. `union mhi_ep_ring_ctx` overlays command/event/channel/generic contexts.

Control flow role: this header describes how endpoint code maps host-owned contexts and doorbells. `main.c` queues work using these structures; `ring.c` starts/resets/cache-updates rings; `mmio.c` reads/writes endpoint registers; `sm.c` transitions MHI states.

State and persistence: in-memory state mirrors host ring pointers and channel states while the endpoint is powered. The actual host contexts live in shared memory mapped through controller `alloc_map()` callbacks.

Dependencies and integration: depends on common MHI protocol definitions and public `mhi_ep` controller/device types. It exposes `mhi_ep_bus_type` to endpoint code and links the endpoint object files.

Risks: interrupt mask registers use inverted naming semantics where writing one enables interrupts; ring offsets and DB register calculations are protocol-critical; channel pairing assumptions live outside this header but depend on `mhi_ep_chan`. Test signals include endpoint power-up, channel doorbells across all mask rows, event ring moderation, command ring processing, reset, suspend/resume, and build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/mhi/ep/internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/mhi/ep/main.c -->
# sources/distributed-fs/ceph-client/drivers/bus/mhi/ep/main.c

Purpose: core MHI endpoint bus stack. It registers endpoint controllers, exposes the `mhi_ep` bus, creates/destroys endpoint client devices on channel start/reset, processes host command/channel doorbells, handles MHI state transitions and resets, and provides data-transfer APIs to endpoint client drivers.

Important APIs: exported `mhi_ep_register_controller()`, `mhi_ep_unregister_controller()`, `mhi_ep_power_up()`, `mhi_ep_power_down()`, `mhi_ep_queue_skb()`, `mhi_ep_queue_is_empty()`, `__mhi_ep_driver_register()`, and `mhi_ep_driver_unregister()`. Internal workers process command rings, channel rings, state transitions, and reset recovery.

Control flow: controller registration validates transport callbacks, initializes channels/caches/workqueue/IRQ, writes MHI version/environment, allocates controller device, and registers it on the bus. Power-up masks interrupts, resets MMIO, initializes rings, enters READY, waits for host M0, maps host contexts, starts command ring, enables interrupts, and enables IRQ. IRQ handling acknowledges control interrupts, schedules reset on host reset, queues state work for M0/M3, queues command ring work on CRDB, and queues channel ring work from channel DB masks.

Transfer behavior: START_CHAN starts a channel ring, sets state RUNNING, sends command completion, creates paired UL/DL client devices on even UL channels, and enables channel DB. UL doorbells trigger async reads from host TRE buffers with callbacks and EOB/EOT events. DL sends use `mhi_ep_queue_skb()` to write skb data into host TREs and send OVERFLOW or EOT completions. STOP/RESET notify clients with `-ENOTCONN`, update channel state, and reset rings.

State and persistence: state spans controller IDA index, controller device, channel array, command/event rings, kmem caches, workqueue, lists, per-channel locks, `enabled`, MHI state, cached host contexts, and dynamic client devices. Reset/power-down tears down transfers, devices, rings, host mappings, interrupts, and event arrays.

Dependencies and integration: depends on endpoint MMIO/ring/state helpers, controller transport callbacks (`read_sync`, `write_sync`, `read_async`, `write_async`, `alloc_map`, `unmap_free`, `raise_irq`), Linux device/bus model, IRQ/workqueue APIs, skbuffs, and public MHI endpoint driver APIs.

Risks: concurrency is complex across IRQ, workqueue, channel locks, event lock, state lock, and async completion callbacks. Dynamic device lifetime relies on paired channel names and reference counts. Partial TD handling is explicitly TODO for DL. Reset recovery only re-powers after SYS_ERR. Test signals include controller register/unregister, power-up/down, M0/M3 transitions, host reset, START/STOP/RESET command completions, paired device probe/remove, UL/DL transfers including chained TREs and overflow, interrupt moderation, and client-driver callback disconnect paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/mhi/ep/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/mhi/ep/mmio.c -->
# sources/distributed-fs/ceph-client/drivers/bus/mhi/ep/mmio.c

Purpose: endpoint MMIO helper layer for reading/writing MHI endpoint registers, managing interrupt masks/status, discovering host context base addresses, reading doorbells, publishing execution environment, and resetting endpoint-visible MHI state.

Important APIs: basic accessors `mhi_ep_mmio_read/write/masked_read/masked_write`; interrupt helpers for control, command DB, channel DB, event DB masking/status; base readers `mhi_ep_mmio_get_chc_base()`, `mhi_ep_mmio_get_erc_base()`, `mhi_ep_mmio_get_crc_base()`; `mhi_ep_mmio_get_db()`; state helpers `mhi_ep_mmio_get_mhi_state()`, `mhi_ep_mmio_set_env()`, `mhi_ep_mmio_clear_reset()`, `mhi_ep_mmio_reset()`, `mhi_ep_mmio_init()`, and `mhi_ep_mmio_update_ner()`.

Control flow: initialization reads CHDB/ERDB offsets and event-ring counts, then clears MHI control/status and all interrupt status. Channel DB enable/disable updates both hardware mask registers and a local mask cache used by IRQ processing. Doorbell reads combine high/low 32-bit registers into host ring write pointers.

State and persistence: maintains cached `chdb[].mask/status`, event ring counts, hardware event ring count, and host physical base addresses in `mhi_ep_cntrl`. Hardware interrupt masks and MHI status persist while endpoint BAR state is powered.

Dependencies and integration: depends on endpoint register offsets from `internal.h`, common masks, `readl/writel`, and `mhi_ep_cntrl->mmio`. It is called by endpoint main, ring, and state-machine code.

Risks: interrupt mask naming is nonstandard: writing 1 enables. Incorrect local mask synchronization drops or processes disabled channel doorbells. MMIO reset clears status and all interrupt bits, so ordering around host reset matters. Test signals include register init, all channel/event mask rows, doorbell high/low composition, host base address reads, MHI reset clear, READY/SYSERR status writes via state code, and IRQ ack/clear behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/mhi/ep/mmio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/mhi/ep/ring.c -->
# sources/distributed-fs/ceph-client/drivers/bus/mhi/ep/ring.c

Purpose: endpoint ring cache and ring-pointer management for command, channel, and event rings. It maps host ring context into local state, caches host descriptors, appends event elements to host rings, updates read pointers, and raises moderated IRQs for event rings.

Important APIs: `mhi_ep_ring_init()`, `mhi_ep_ring_start()`, `mhi_ep_ring_reset()`, `mhi_ep_ring_addr2offset()`, `mhi_ep_update_wr_offset()`, `mhi_ep_ring_add_element()`, and `mhi_ep_ring_inc_index()`. Internal caching copies host descriptors through controller `read_sync()` and writes event elements through `write_sync()`.

Control flow: ring start reads `rlen`, `rbase`, `rp`, and `wp` from host context, computes offsets, records event MSI vector/intmod, allocates a descriptor cache, and caches descriptors up to host write pointer. Channel/command rings refresh their cached descriptors when doorbells arrive. Adding an event checks free space, writes a ring element to the host event ring, increments the local read offset, and writes the new `rp` back to the context. Event-ring delayed work raises the configured IRQ vector.

State and persistence: `struct mhi_ep_ring` stores ring size/base, read/write offsets, descriptor cache, event moderation work, IRQ pending flag, and started state. Host ring contexts persist in shared memory; cache is freed on reset.

Dependencies and integration: depends on controller read/write sync transport callbacks, MMIO doorbell reads, endpoint main event/command/channel processing, and delayed work.

Risks: wraparound cache copying and free-space calculation are protocol-critical. `mhi_ep_ring_add_element()` supports one element at a time only. Event ring start does not cache descriptors. Test signals include wraparound descriptor reads, empty/full event ring behavior, rp/wp updates, event interrupt moderation/cancel, reset cancellation of delayed work, and transport callback failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/mhi/ep/ring.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/mhi/ep/sm.c -->
# sources/distributed-fs/ceph-client/drivers/bus/mhi/ep/sm.c

Purpose: endpoint MHI state-machine helpers. It validates and performs RESET->READY, READY/M3->M0, M0->M3, and any-state->SYS_ERR transitions, writes endpoint status registers, sends state/environment events, and suspends or resumes channels around low-power transitions.

Important APIs: `mhi_ep_check_mhi_state()`, `mhi_ep_set_mhi_state()`, `mhi_ep_set_m0_state()`, `mhi_ep_set_m3_state()`, and `mhi_ep_set_ready_state()`.

Control flow: validation allows SYS_ERR from any state, READY only from RESET, M0 from READY or M3, and M3 from M0. `mhi_ep_set_mhi_state()` writes MHISTATUS state bits and READY/SYSERR bits. M0 transition resumes suspended channels if coming from M3, sends state-change event, and sends AMSS EE event when coming from READY. M3 transition updates state, suspends running channels, and sends state-change event. READY transition first verifies host-visible MHISTATUS is RESET and not already READY.

State and persistence: updates `mhi_cntrl->mhi_state`, channel states through main helpers, and hardware MHISTATUS bits. State is runtime-only and reset clears it.

Dependencies and integration: depends on endpoint MMIO helpers, event senders in `main.c`, channel suspend/resume helpers, `state_lock`, and SYS_ERR handling.

Risks: M1/M2 are explicitly unsupported. Failed M0/M3 transitions trigger SYS_ERR handling. READY requires host status to be reset, so ordering with host reset completion matters. Test signals include allowed and forbidden transitions, READY bit setting, SYSERR bit setting, M0 from READY versus M3, M3 suspend behavior, M0 resume behavior, and event-send failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/mhi/ep/sm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/mhi/host/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/bus/mhi/host/Kconfig

Purpose: declares host-side MHI configuration symbols: the core bus, optional debugfs support, and generic PCI controller driver.

Important declarations: `CONFIG_MHI_BUS` builds the MHI host stack; `CONFIG_MHI_BUS_DEBUG` depends on `MHI_BUS && DEBUG_FS`; `CONFIG_MHI_BUS_PCI_GENERIC` depends on `MHI_BUS` and `PCI`.

Control flow and state: configuration-time only. These symbols control compilation of host core, debugfs, and PCI controller objects.

Dependencies and integration: connects the MHI host protocol stack to kernel debugfs and PCI support. The generic PCI driver covers Qualcomm SDX-class PCIe modems per help text.

Risks and tests: dependency mistakes can create build/link failures or missing debugfs files. Test signals include allmodconfig, host core built-in/module, debugfs enabled/disabled, PCI generic enabled without endpoint, and help/menu visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/mhi/host/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/mhi/host/Makefile -->
# sources/distributed-fs/ceph-client/drivers/bus/mhi/host/Makefile

Purpose: builds host-side MHI objects and the optional generic PCI controller.

Important declarations: `mhi-y := init.o main.o pm.o boot.o`; `mhi-$(CONFIG_MHI_BUS_DEBUG) += debugfs.o`; `obj-$(CONFIG_MHI_BUS_PCI_GENERIC) += mhi_pci_generic.o`; `mhi_pci_generic-y += pci_generic.o`.

Control flow and state: build aggregation only. It ensures firmware boot support is always part of the host core and debugfs is conditional.

Dependencies and integration: driven by `CONFIG_MHI_BUS`, `CONFIG_MHI_BUS_DEBUG`, and `CONFIG_MHI_BUS_PCI_GENERIC`. Links with shared common headers and public MHI APIs.

Risks and tests: missing object entries would remove runtime functionality such as firmware loading or debugfs. Test signals include host core link, debugfs symbol inclusion/exclusion, and generic PCI module builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/mhi/host/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/mhi/host/boot.c -->
# sources/distributed-fs/ceph-client/drivers/bus/mhi/host/boot.c

Purpose: host-side MHI boot and firmware image transfer support. It allocates BHI/BHIE DMA buffers, loads firmware through BHI or BHIE vector interfaces, handles firmware boot continuation, prepares/downloads RDDM crash dumps, and transitions the controller toward READY/mission mode.

Important APIs: `mhi_rddm_prepare()`, `mhi_download_rddm_image()`, `mhi_alloc_bhie_table()`, `mhi_free_bhie_table()`, `mhi_fw_load_handler()`, and `mhi_download_amss_image()`. Internal helpers allocate BHI buffers, copy firmware into segmented BHIE vectors, choose BHI/BHIE/FBC load mode, and dump BHI error registers.

Control flow: firmware handler reads hardware serial number, skips loading if current EE is already pass-through, selects EDL or normal firmware, accepts pre-supplied firmware data for FBC, requests firmware if needed, transfers SBL over BHI/BHIE, resets device state, optionally prepares full firmware BHIE vectors for FBC, releases firmware, and calls `mhi_ready_state_transition()`. AMSS download later rings BHIE TX vector DB using the prepared table.

RDDM behavior: preparation fills vector table entries and programs RXVEC registers. Normal RDDM waits on `state_event`; panic path avoids locks where unsafe, forces SYS_ERR/reset if needed, and polls registers with udelay.

State and persistence: stores DMA-coherent image buffers in `struct image_info`, controller serial number, `fbc_image`, PM state, device state, and waitqueue-observed BHIE/BHI status. Buffers are freed on errors or later cleanup.

Dependencies and integration: depends on firmware loader, DMA coherent allocation, MHI register helpers, PM locks/states, wait queues, random nonzero sequence IDs, BHI/BHIE register definitions, and controller callbacks such as `mhi_soc_reset()`.

Risks: firmware size/segment metadata must be consistent; FBC combined ELF handling assumes a second ELF header after `sbl_size`; panic RDDM deliberately bypasses normal locking; timeout/status handling drives PM error states. Test signals include BHI and BHIE boot, FBC staged boot, EDL image path, missing firmware errors, BHI error dump, AMSS transfer, RDDM normal and panic download, timeout, PM error wakeups, and DMA cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/mhi/host/boot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/mhi/host/debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/bus/mhi/host/debugfs.c

Purpose: debugfs diagnostics and controls for MHI host controllers. It exposes controller state, event rings, channels, devices, selected register dumps, device wake votes, and timeout tuning under a per-controller debugfs directory.

Important APIs: `mhi_debugfs_init()` creates the root directory, `mhi_create_debugfs()` creates per-controller files, `mhi_destroy_debugfs()` removes them, and `mhi_debugfs_exit()` removes the root. File operations use `single_open()` and seq_file show helpers. Writable files are `device_wake` and `timeout_ms`.

Control flow: state/events/channels/devices show functions first validate active state when needed, then print controller PM/device/MHI/EE state, counters, event ring contexts, channel contexts, child MHI devices, or register values. `device_wake` accepts `get`/`put` to call `mhi_device_get_sync()` or `mhi_device_put()`. `timeout_ms` parses a u32 and updates controller timeout.

State and persistence: debugfs files expose live controller fields and can mutate `timeout_ms` and device wake votes. No state persists across unload/reboot. `debugfs_dentry` is tracked in the controller.

Dependencies and integration: depends on debugfs, seq_file, MHI host internals, register access helpers, PM-state validity macros, device model child traversal, and string helpers.

Risks: writable debug controls can affect runtime power state and timeout behavior, so this is gated by debugfs configuration rather than production ABI. Register dumps require valid PM/register-access state. Test signals include debugfs directory creation/removal, reads when active/inactive, wake get/put behavior, timeout writes including invalid input, event/channel ring formatting, register read failures, and controller removal while files exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/mhi/host/debugfs.c -->
