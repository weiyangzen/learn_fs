# subset-b-001294 research

Grouped research for the FPGA framework, DFL enumeration, FPGA manager implementations, and FPGA KUnit build hooks under `sources/distributed-fs/ceph-client/drivers/fpga`. Each section is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/dfl-n3000-nios.c -->
# sources/distributed-fs/ceph-client/drivers/fpga/dfl-n3000-nios.c

Purpose: implements a DFL bus driver for the Intel PAC N3000 Nios private feature. It exposes Nios firmware, retimer, and FEC status through sysfs, waits for the Nios firmware to finish one-time board initialization, then instantiates an Altera SPI controller and MAX10 BMC SPI child so the host can access or recover board-management firmware.

Important APIs, types, and functions: `struct n3000_nios` stores the DFL MMIO base, regmap, owning device, and created `subdev_spi_altera` platform device. `n3000_nios_probe` maps `ddev->mmio_res`, builds a custom regmap over the Nios indirect register bus, calls `n3000_nios_init_done_check`, and registers the SPI controller. Sysfs attributes `nios_fw_version`, `retimer_A_mode`, `retimer_B_mode`, and `fec_mode` read Nios registers through that regmap. `n3000_nios_reg_read` and `n3000_nios_reg_write` encode indirect read/write commands in `N3000_NS_CTRL` and poll `N3000_NS_STAT_RW_VAL`. The driver binds to DFL devices `{ FME_ID, FME_FEATURE_ID_N3000_NIOS }`.

Control flow: probe is synchronous. It initializes the regmap, reads the Nios firmware version, optionally asserts `INIT_START` for firmware major version 3 or later, requests RS FEC for all links, and polls `NIOS_INIT_DONE` for up to ten seconds. Even missing firmware or failed retimer initialization is treated as recoverable in some paths so the SPI controller can be created and the BMC can be used to restore firmware. Remove unregisters the child SPI controller.

State and persistence: persistent state is hardware-resident in Nios init/version/mode registers and in the created child platform device. Linux state is devm-managed private data, regmap, sysfs group, and the `altera_spi` pointer. No settings are persisted by the driver other than writing the Nios init/FEC request register during initialization.

Dependencies and integration points: depends on the DFL bus, MMIO `readq`/`writeq`, `regmap`, Altera SPI platform data, SPI board info for `m10-n3000`, and the MAX10 BMC stack. It is an FME private-feature driver, so DFL enumeration in `dfl.c` and PCI discovery in `dfl-pci.c` must expose the private feature first.

Risks and test signals: risks include tight polling on the indirect bus without time-based delay, hardware-version-specific init semantics, continuing after missing Nios firmware, and treating inconsistent FEC fields as `-EFAULT`. Test signals are DFL driver binding, visible sysfs attributes, successful `subdev_spi_altera` creation, `m10-n3000` SPI child probing, correct firmware version formatting, and recovery behavior when Nios firmware or retimer status is bad.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/dfl-n3000-nios.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/dfl-pci.c -->
# sources/distributed-fs/ceph-client/drivers/fpga/dfl-pci.c

Purpose: PCIe front-end for Intel and Silicom FPGA devices that expose Device Feature Lists. It enables the PCI device, configures DMA and MSI-X, discovers DFL MMIO ranges either from Intel VSEC records or legacy BAR0/FME port-offset registers, and asks the DFL core to create container, FME, port, AFU, and private-feature devices.

Important APIs and functions: `cci_pcie_id_tbl` matches PF and VF device IDs for Intel PACs, D5005/N3000/N6000/N6001/C6100, and Silicom PAC N5010/N5011. `cci_pci_probe` uses `pcim_enable_device`, `pci_set_master`, DMA mask negotiation, and `cci_enumerate_feature_devs`. `find_dfls_by_vsec` parses vendor-specific capability `PCI_VSEC_ID_INTEL_DFLS`, validates BAR indicators and offsets, and records each DFL range in `dfl_fpga_enum_info`. `find_dfls_by_default` maps BAR0, detects FME or Port headers, and for PFs walks FME port-offset registers. `cci_pci_sriov_configure` coordinates SR-IOV enable/disable with DFL port access-mode helpers.

Control flow: probe prepares PCI resources, creates driver data, allocates all MSI-X vectors if present, constructs a Linux IRQ table, discovers DFL ranges, and calls `dfl_fpga_feature_devs_enumerate`. VSEC discovery is preferred; default BAR0 discovery is fallback. Remove disables SR-IOV for PFs, removes DFL feature devices, and frees IRQ vectors.

State and persistence: driver state is `struct cci_drvdata` with the DFL container pointer and PCI-managed resources. Device state includes MSI-X vector allocation, DMA mask, bus mastering, SR-IOV enablement, and FME port access-mode bits. It does not persist configuration across reboot.

Dependencies and integration points: depends on the PCI subsystem, MSI-X support, DFL core enumeration APIs, DFL header helpers from `dfl.h`, and SR-IOV core callbacks. It supplies the physical MMIO and IRQ inventory consumed by `dfl.c`; downstream FME, port, and DFL bus drivers bind after enumeration.

Risks and test signals: risks include malformed VSEC bounds, duplicate BAR records, legacy discovery assuming BAR0 starts with a valid DFL header, `WARN_ON` rather than hard failure for excessive port count, and SR-IOV requiring user-space to release exactly one port per VF. Test signals are PCI probe logs, correct `fpga_region`, `dfl-fme`, `dfl-port`, and `dfl_dev.*` children, MSI-X interrupt delivery, VF creation after port release, and clean remove with SR-IOV disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/dfl-pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/dfl.c -->
# sources/distributed-fs/ceph-client/drivers/fpga/dfl.c

Purpose: core support for FPGA Device Feature List enumeration and the DFL bus. It turns raw DFL MMIO ranges and IRQ tables into a container FPGA region, platform devices for FME and ports, DFL bus devices for individual subfeatures, character-device numbers, port-operation registration, SR-IOV port release/assign operations, and eventfd-backed interrupt ioctls.

Important APIs, types, and functions: global device metadata is held in `dfl_devs` and `dfl_chrdevs`. The exported bus API includes `__dfl_driver_register`, `dfl_driver_unregister`, `dfh_find_param`, `dfl_fpga_enum_info_alloc`, `dfl_fpga_enum_info_add_dfl`, `dfl_fpga_enum_info_add_irq`, `dfl_fpga_feature_devs_enumerate`, and `dfl_fpga_feature_devs_remove`. Platform-device APIs include `dfl_fpga_dev_feature_init`, `dfl_fpga_dev_feature_uinit`, `dfl_fpga_dev_ops_register`, and `dfl_fpga_dev_ops_unregister`. SR-IOV helpers are `dfl_fpga_cdev_release_port`, `dfl_fpga_cdev_assign_port`, `dfl_fpga_cdev_config_ports_pf`, and `dfl_fpga_cdev_config_ports_vf`. IRQ helpers are `dfl_fpga_set_irq_triggers`, `dfl_feature_ioctl_get_num_irqs`, and `dfl_feature_ioctl_set_irq`.

Control flow: PCI or another parent builds `dfl_fpga_enum_info`; `dfl_fpga_feature_devs_enumerate` registers a base FPGA region, allocates a `build_feature_devs_info`, and parses each DFL range. `parse_feature_list` walks DFH entries until EOL or zero offset. FIU headers start new FME/port platform devices; private features and AFUs are attached as subfeatures. DFHv1 parameter blocks are copied and used for MSI-X metadata; DFHv0 interrupt metadata is read from feature-specific registers. Once a FIU's feature list is complete, `feature_dev_register` creates the `dfl-fme` or `dfl-port` platform device. Later, platform drivers initialize known subfeatures and unmapped subfeatures become DFL bus devices.

State and persistence: global state includes IDRs for FME/port platform IDs, an IDA for DFL bus devices, a DFL bus type, char-device major ranges, and the global port-ops list. Per-container state is `struct dfl_fpga_cdev`, with an FPGA region, FME device reference, port list, lock, and released-port count. Per-feature-device state tracks open/exclusive-use counts, resources, private data, subfeatures, and IRQ contexts. State is in-memory plus hardware MMIO mutations for port PF/VF access mode.

Dependencies and integration points: depends on DFL register definitions in `dfl.h`, FPGA region registration, platform bus, character devices, eventfd, IRQ core, devres, IDR/IDA, and user-copy helpers. It integrates PCI enumeration with FME/port platform drivers and DFL private-feature drivers.

Risks and test signals: risks include trusting hardware-provided offsets/sizes, DFHv1 parameter-chain validation gaps, resource insertion conflicts, eventfd IRQ lifetime complexity, global port-ops name matching, and SR-IOV access-mode transitions needing precise sequencing. Test signals include DFL bus modaliases, sysfs `type` and `feature_id`, correct platform resources, KUnit/framework coverage, port release/assign ioctl workflows, eventfd interrupts, and error-path cleanup after malformed DFL input.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/dfl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/dfl.h -->
# sources/distributed-fs/ceph-client/drivers/fpga/dfl.h

Purpose: internal header for the DFL framework and DFL-aware drivers. It centralizes DFH/FME/Port register definitions, feature IDs, bit masks, core data structures, inline helpers, and exported prototypes used by `dfl.c`, PCI enumeration, FME/port drivers, private-feature drivers, and SR-IOV/IRQ helpers.

Important APIs and types: register definitions cover common DFH fields, DFHv1 CSR and parameter records, FME capability/port-offset/error registers, and Port capability/control/status/error/user-interrupt registers. Key structures include `dfl_fpga_port_ops`, `dfl_feature_id`, `dfl_feature_driver`, `dfl_feature_irq_ctx`, `dfl_feature`, `dfl_feature_dev_data`, `dfl_feature_platform_data`, `dfl_feature_ops`, `dfl_fpga_enum_info`, `dfl_fpga_enum_dfl`, and `dfl_fpga_cdev`. Inline helpers implement feature-use accounting, private-data access, feature iteration, feature lookup by ID, conversion from inode/device to DFL data, parent lookup, and FME/Port DFH detection.

Control flow role: the header itself has no runtime entry point, but it defines the contracts that make DFL enumeration multi-stage. Parent bus drivers create `dfl_fpga_enum_info`; the core creates `dfl_feature_dev_data`; platform drivers bind to FME/port devices and initialize subfeatures through `dfl_feature_driver` and `dfl_feature_ops`; private subfeatures may become `struct dfl_device` instances on the DFL bus.

State and persistence: no storage is allocated in the header, but it describes all major in-memory state fields, including open/exclusive-use tracking, port disable counts, platform resources, IRQ eventfd contexts, FPGA-region container links, and released-port counters. Hardware-persistent state is represented only as register offsets and masks.

Dependencies and integration points: depends on Linux bitfield, cdev, eventfd, interrupt, iopoll, platform-device, UUID, and FPGA region headers. It is tightly coupled to the DFL ABI in `<linux/dfl.h>` and the register layout understood by Intel FPGA hardware.

Risks and test signals: risks include duplicated hardware constants becoming stale, inline use-count helpers requiring external locking, `dfl_get_feature_ioaddr_by_id` warning and returning NULL when callers assume presence, and global assumptions such as `MAX_DFL_FPGA_PORT_NUM` being four. Test signals are compile coverage across DFL core and drivers, successful modalias matching, correct register decoding on hardware, and SR-IOV/IRQ workflows using the declared APIs without lockdep or lifetime warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/dfl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/fpga-bridge.c -->
# sources/distributed-fs/ceph-client/drivers/fpga/fpga-bridge.c

Purpose: generic FPGA bridge class and helper library. It registers bridge devices, exposes their name/state through sysfs, provides exclusive get/put semantics, and lets FPGA regions disable and re-enable one or more bridges around reconfiguration.

Important APIs and functions: exported operations include `fpga_bridge_enable`, `fpga_bridge_disable`, `of_fpga_bridge_get`, `fpga_bridge_get`, `fpga_bridge_put`, `fpga_bridges_enable`, `fpga_bridges_disable`, `fpga_bridges_put`, `of_fpga_bridge_get_to_list`, `fpga_bridge_get_to_list`, `__fpga_bridge_register`, and `fpga_bridge_unregister`. `struct fpga_bridge` instances are registered under the `fpga_bridge` class with IDA-assigned IDs and optional low-level ops groups. `__fpga_bridge_get` stores image info, locks the bridge mutex, and takes the owner module reference.

Control flow: low-level bridge drivers call `fpga_bridge_register`. Region code collects bridge references by OF node or parent device and adds them to a list. Programming disables the list, loads the FPGA image, and enables the list. On post-remove or cleanup, `fpga_bridges_put` releases each bridge and removes it from the list under a spinlock.

State and persistence: global state is the bridge class, IDA, and `bridge_list_lock`. Per-bridge state includes name, ops, owner module, private pointer, mutex, list node, and transient `info` pointer. Hardware state is whatever the low-level `enable_set`, `enable_show`, or `fpga_bridge_remove` callbacks implement.

Dependencies and integration points: depends on the device class infrastructure, OF platform population, IDA, module refs, mutexes, spinlocks, and `<linux/fpga/fpga-bridge.h>`. It is consumed by `fpga-region.c` and `of-fpga-region.c` and by low-level bridge drivers outside this subset.

Risks and test signals: risks include list manipulation while bridge devices are being unregistered, bridge callbacks being optional, `info` being shared transiently with low-level drivers, and exclusive locking causing `-EBUSY` on overlapping reconfiguration. Test signals are `/sys/class/fpga_bridge/br*/name` and `state`, KUnit bridge tests, successful OF bridge acquisition, bridge disable/enable ordering during region programming, and clean put/unregister without module ref leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/fpga-bridge.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/fpga-mgr.c -->
# sources/distributed-fs/ceph-client/drivers/fpga/fpga-mgr.c

Purpose: generic FPGA manager framework. It registers FPGA manager devices, serializes programming, loads images from firmware, linear buffers, or scatter-gather tables, drives low-level manager callbacks through parse/init/write/complete phases, and exposes manager name, state, and status through sysfs.

Important APIs and functions: exported APIs include `fpga_image_info_alloc`, `fpga_image_info_free`, `fpga_mgr_load`, `fpga_mgr_get`, `of_fpga_mgr_get`, `fpga_mgr_put`, `fpga_mgr_lock`, `fpga_mgr_unlock`, `__fpga_mgr_register_full`, `__fpga_mgr_register`, `fpga_mgr_unregister`, `__devm_fpga_mgr_register_full`, and `__devm_fpga_mgr_register`. Core loading helpers include `fpga_mgr_parse_header_mapped`, `fpga_mgr_parse_header_sg_first`, `fpga_mgr_parse_header_sg`, `fpga_mgr_prepare_sg`, `fpga_mgr_buf_load_sg`, `fpga_mgr_buf_load_mapped`, `fpga_mgr_buf_load`, and `fpga_mgr_firmware_load`.

Control flow: callers fill `struct fpga_image_info` with an SG table, buffer, or firmware name. `fpga_mgr_load` seeds `header_size` from low-level ops and selects a load path. The framework parses headers, calls `write_init`, writes data through either `write_sg` or repeated `write`, optionally skips headers and honors parsed `data_size`, then calls `write_complete`. State transitions move through firmware request, parse header, write init, write, write complete, operating, or error variants.

State and persistence: global state is the `fpga_manager` class and IDA. Per-manager state includes low-level ops, private data, compat ID, owner module, class device, `ref_mutex`, and current framework state. Image info is devm-managed and may contain firmware name, buffer, SG table, flags, header/data sizes, timeouts, and overlay references. No configuration persists except hardware state changed by low-level drivers.

Dependencies and integration points: depends on firmware loader, scatterlist mapping, highmem helpers, device classes, OF lookup, mutexes, and low-level manager drivers such as iCE40, Lattice sysCONFIG, Microchip, SoCFPGA, Arria10, and Stratix10. `fpga-region.c` is the primary orchestrator consumer.

Risks and test signals: risks include header-size growth loops for SG parsing, malformed parsed `data_size`, low-level drivers with only `write_sg` requiring page conversion, status string indexing assuming valid states, and callers needing explicit `fpga_mgr_lock`. Test signals are KUnit manager tests, sysfs state/status, firmware request failures, buffer and SG programming paths, low-level callback error transitions, and absence of refcount/module leaks on get/put/register/unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/fpga-mgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/fpga-region.c -->
# sources/distributed-fs/ceph-client/drivers/fpga/fpga-region.c

Purpose: generic FPGA region class. A region ties an FPGA manager, optional compatibility ID, private data, and optional bridge acquisition callback into a programmable unit that can safely load an image while bridge traffic is disabled.

Important APIs and functions: exported APIs are `fpga_region_class_find`, `fpga_region_program_fpga`, `__fpga_region_register_full`, `__fpga_region_register`, and `fpga_region_unregister`. `fpga_region_get` and `fpga_region_put` are internal exclusive-reference helpers that lock the region mutex and hold the owner module. Sysfs `compat_id` exposes a 128-bit compatibility identifier if provided.

Control flow: registration allocates an IDA ID, initializes the bridge list and mutex, sets class/parent/OF node, and registers `regionN`. Programming gets the region exclusively, locks the FPGA manager, optionally invokes `get_bridges`, disables collected bridges, calls `fpga_mgr_load(region->mgr, region->info)`, enables bridges, unlocks the manager, and puts the region. On error after bridge collection, dynamic bridge lists are put and manager/region locks are released.

State and persistence: global state is the `fpga_region` class and IDA. Per-region state includes manager pointer, compat ID, private pointer, bridge list, `get_bridges` callback, module owner, current image info pointer owned by callers such as OF overlay code, and a mutex. Bridge references can remain held after successful programming when the region-specific callback collected them, so the overlay lifecycle can prevent unsafe reprogramming.

Dependencies and integration points: depends on FPGA manager and bridge frameworks, device classes, lists, IDA, module refs, and `<linux/fpga/fpga-region.h>`. Used directly by DFL core for container regions and by OF support for device-tree controlled programming.

Risks and test signals: risks include successful programming intentionally retaining bridge references until caller cleanup, caller-owned `region->info` lifetime, exclusive mutex causing `-EBUSY`, and error paths that differ depending on whether bridges were pre-provided or dynamically collected. Test signals are `/sys/class/fpga_region/region*/compat_id`, KUnit region tests, manager lock contention behavior, correct bridge disable/load/enable ordering, and cleanup during failed loads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/fpga-region.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/ice40-spi.c -->
# sources/distributed-fs/ceph-client/drivers/fpga/ice40-spi.c

Purpose: FPGA manager driver for configuring Lattice iCE40 SRAM over slave SPI. It controls CRESET_B and observes CDONE GPIO while using the SPI bus to stream the bitstream and activation clocks.

Important APIs and functions: `struct ice40_fpga_priv` holds the SPI device and `reset`/`cdone` GPIO descriptors. `ice40_fpga_ops_state` reports operating when CDONE is asserted. `ice40_fpga_ops_write_init` rejects partial reconfiguration, locks the SPI bus, asserts reset and chip select long enough for reset timing, releases reset, verifies CDONE deasserted, performs housekeeping delay, and unlocks. `ice40_fpga_ops_write` calls `spi_write`, and `ice40_fpga_ops_write_complete` requires CDONE asserted then sends zero padding bytes for activation.

Control flow: probe validates SPI max/min speed and CPHA, obtains required GPIOs, and registers a devm FPGA manager. The manager framework calls write-init, write, and write-complete during image load. There is no explicit remove beyond devm cleanup.

State and persistence: Linux state is the SPI device pointer and two GPIO descriptors. Hardware state is volatile SRAM configuration, reset line, CDONE pin, and SPI bus transactions. No bitstream metadata is parsed and no settings persist across power loss.

Dependencies and integration points: depends on SPI core, gpiod consumer API, FPGA manager framework, OF compatible `lattice,ice40-fpga-mgr`, and SPI device ID `ice40-fpga-mgr`.

Risks and test signals: risks include board-specific GPIO polarity requirements, SPI speed/mode misconfiguration, failure to deassert CDONE during reset, CDONE asserted before activation padding is sent, and no support for partial reconfiguration. Test signals are manager registration, successful state transition to operating, expected reset/CDONE timing on a logic analyzer, SPI transfer success, and failure returns when CDONE remains low after transfer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/ice40-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/intel-m10-bmc-sec-update.c -->
# sources/distributed-fs/ceph-client/drivers/fpga/intel-m10-bmc-sec-update.c

Purpose: Intel MAX10 BMC secure-update driver. It exposes BMC security telemetry through sysfs and registers a firmware-upload endpoint that stages a secure image into MAX10 flash staging space, coordinates RSU handshakes with Nios/BMC firmware, and polls authentication/programming completion.

Important APIs and functions: `struct m10bmc_sec` stores the parent `intel_m10bmc`, firmware-upload handle/name, xarray ID, cancel flag, and per-device RSU status ops. `m10bmc_sec_read` and `m10bmc_sec_write` access flash through optional bulk ops or regmap stride-aware operations. Sysfs helpers expose root-entry hashes, canceled CSKs, and flash update count. Firmware-upload callbacks are `m10bmc_sec_prepare`, `m10bmc_sec_fw_write`, `m10bmc_sec_poll_complete`, `m10bmc_sec_cancel`, and `m10bmc_sec_cleanup`. Status helpers differentiate N3000/D5005 doorbell status from N6000 auth-result status.

Control flow: probe allocates a unique `secure-updateN` name, registers firmware upload, and installs security attributes. Prepare validates size, optionally locks flash writes, checks idle RSU state, sets firmware state to prepare, requests RSU, waits for ready, handles cancellation, and transitions to write state. Write sends chunks up to `WRITE_BLOCK_SIZE` while RSU progress remains ready. Poll-complete marks host write done, waits for RSU progress to leave ready, checks status, then polls until done or timeout. Cleanup cancels if possible, returns firmware state to normal, and unlocks flash.

State and persistence: persistent hardware state includes security hashes, CSK cancellation vectors, flash update count, staging flash contents, doorbell, auth result, and BMC firmware state. Linux state includes the global firmware-upload xarray, firmware-upload object, generated name, cancel flag, and flash lock ownership. Cancel is intentionally asynchronous only as a flag and is synchronized by normal callback flow.

Dependencies and integration points: depends on firmware-upload API, Intel MAX10 BMC MFD core, CSR maps, regmap, optional flash bulk ops, xarray allocation, platform device IDs `n3000bmc-sec-update`, `d5005bmc-sec-update`, and `n6000bmc-sec-update`.

Risks and test signals: risks include stride-aligned staging writes, update-size bounds, long RSU timeouts, ambiguous hardware status mapping across board generations, cancellation only when RSU is ready, flash wearout status, and sysfs bitmap casting assumptions for flash count. Test signals are security sysfs values, firmware-upload device creation, successful prepare/write/poll-complete, flash lock/unlock behavior, expected error codes for wearout/timeout/auth failure, and cleanup after cancel.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/intel-m10-bmc-sec-update.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/lattice-sysconfig-spi.c -->
# sources/distributed-fs/ceph-client/drivers/fpga/lattice-sysconfig-spi.c

Purpose: SPI transport adapter for the generic Lattice sysCONFIG FPGA manager core. It supplies command-transfer and bitstream-burst callbacks, enforces ECP5 SPI speed limits, and delegates common programming behavior to `sysconfig_probe`.

Important APIs and functions: `sysconfig_spi_cmd_transfer` implements command reads/writes with `spi_write_then_read`. `sysconfig_spi_bitstream_burst_init` sends `SYSCONFIG_LSC_BITSTREAM_BURST`, locks the SPI bus, and keeps chip select asserted for the burst. `sysconfig_spi_bitstream_burst_write` streams locked transfers with `cs_change`. `sysconfig_spi_bitstream_burst_complete` unlocks the bus and toggles chip select using a zero-length `spi_write`. `sysconfig_spi_probe` fills `struct sysconfig_priv` callbacks and calls `sysconfig_probe`.

Control flow: probe allocates private data, gets the max speed from OF match data or SPI ID data, rejects over-speed devices, attaches transport callbacks, and registers the common manager. During programming, the common core enters ISC mode and calls the SPI burst callbacks to hold bus ownership until bitstream completion.

State and persistence: this file owns no persistent hardware state beyond SPI bus locking during a burst. Its private data is devm-managed and embedded in the common sysCONFIG manager state. Hardware programming persistence depends on the target Lattice device.

Dependencies and integration points: depends on SPI core, OF match data, `lattice-sysconfig.h`, and the exported `sysconfig_probe` from `lattice-sysconfig.c`. It matches `lattice,sysconfig-ecp5` and SPI ID `sysconfig-ecp5`.

Risks and test signals: risks include bus lock leaks if burst init succeeds but common completion is not called, max-speed driver-data casts, and controller behavior for zero-length CS toggles. Test signals are successful manager registration, rejected too-fast SPI settings, correct CS hold across burst writes, sysCONFIG status polling in the common core, and no SPI bus lock after failed writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/lattice-sysconfig-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/lattice-sysconfig.c -->
# sources/distributed-fs/ceph-client/drivers/fpga/lattice-sysconfig.c

Purpose: common Lattice sysCONFIG FPGA manager logic independent of the transport. It sequences refresh/program mode, ISC enable/erase, address initialization, bitstream burst write, status polling, finish, and cleanup for devices such as ECP5.

Important APIs and functions: transport callbacks are invoked through `struct sysconfig_priv`. Core helpers include `sysconfig_cmd_write`, `sysconfig_cmd_read`, `sysconfig_read_busy`, `sysconfig_poll_busy`, `sysconfig_read_status`, `sysconfig_poll_status`, `sysconfig_refresh`, `sysconfig_isc_enable`, `sysconfig_isc_erase`, `sysconfig_lsc_init_addr`, `sysconfig_bitstream_burst_write`, `sysconfig_isc_finish`, and `sysconfig_cleanup`. FPGA manager ops are `sysconfig_ops_state`, `sysconfig_ops_write_init`, `sysconfig_ops_write`, and `sysconfig_ops_write_complete`. `sysconfig_probe` validates callbacks, gets optional PROGRAM/INIT/DONE GPIOs, and registers the manager.

Control flow: write-init rejects partial reconfiguration, enters program mode through GPIO refresh if all GPIOs exist or LSC refresh otherwise, enables ISC, erases, initializes the address shift register, and starts burst mode. Write streams bitstream chunks through the transport. Write-complete closes burst mode, waits not busy, verifies DONE/status or DONE GPIO, disables ISC, and invokes cleanup on failure. State reports operating through DONE GPIO when present or the status DONE bit otherwise.

State and persistence: state is `struct sysconfig_priv`, optional GPIO descriptors, and transport callbacks. Hardware state includes sysCONFIG command mode, busy/status bits, optional PROGRAM/INIT/DONE pins, flash/SRAM configuration state, and the target bitstream contents.

Dependencies and integration points: depends on FPGA manager core, gpiod, iopoll, delay helpers, and transport-specific modules such as `lattice-sysconfig-spi.c`. It exports `sysconfig_probe` for those transports.

Risks and test signals: risks include optional GPIO combinations changing refresh semantics, cleanup issuing erase/refresh after partial failures, status-error bit interpretation, and transport completion being required to release bus resources. Test signals are manager state from DONE/status, successful ISC enable/erase sequence, polling timeouts, cleanup after injected transport errors, and registration failure when callbacks are missing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/lattice-sysconfig.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/lattice-sysconfig.h -->
# sources/distributed-fs/ceph-client/drivers/fpga/lattice-sysconfig.h

Purpose: private interface shared by the Lattice sysCONFIG common core and transport drivers. It defines sysCONFIG command bytes, status bits, polling constants, transport callback structure, and the common `sysconfig_probe` entry point.

Important APIs and types: command macros include ISC enable/disable/erase, read status, check busy, refresh, init address, and bitstream burst. Status macros cover DONE, BUSY, FAIL, and ERR fields. Poll constants set 30 microsecond intervals, one-second busy timeout, and 100 millisecond GPIO timeout. `struct sysconfig_priv` stores optional PROGRAM/INIT/DONE GPIOs, the owning device, command-transfer callback, and bitstream burst init/write/complete callbacks.

Control flow role: transport drivers allocate and fill `struct sysconfig_priv`, then call `sysconfig_probe`. The common core uses the callbacks to issue commands and stream bitstreams while using the optional GPIOs and status bits defined here to decide state and completion.

State and persistence: no storage is allocated in the header. It defines the in-memory state contract between common and transport code and encodes hardware command/status values for persistent or SRAM configuration on Lattice devices.

Dependencies and integration points: relies on `BIT`, `GENMASK`, `struct gpio_desc`, and `struct device` declarations being available through included users. It is included by `lattice-sysconfig.c` and `lattice-sysconfig-spi.c`.

Risks and test signals: risks include stale opcode/status definitions, callback contract drift, and timeout constants being inappropriate for some boards. Test signals are compile coverage for common and SPI modules, successful callback validation, correct status-bit interpretation, and transport-specific tests that verify command byte sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/lattice-sysconfig.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/machxo2-spi.c -->
# sources/distributed-fs/ceph-client/drivers/fpga/machxo2-spi.c

Purpose: FPGA manager for loading Lattice MachXO2 firmware over slave SPI using sysCONFIG programming commands. It erases/programs nonvolatile configuration pages, issues program-done and refresh commands, and reports operating state from the MachXO2 status register.

Important APIs and functions: command definitions include `ISC_ENABLE`, `ISC_ERASE`, `LSC_INITADDRESS`, `LSC_PROGINCRNV`, `ISC_PROGRAMDONE`, `LSC_REFRESH`, and `LSC_READ_STATUS`. `get_status` performs command+read SPI messages and converts big-endian status. `wait_until_not_busy` polls BUSY with a bounded loop. Manager ops are `machxo2_spi_state`, `machxo2_write_init`, `machxo2_write`, and `machxo2_write_complete`. `machxo2_cleanup` erases and refreshes after failures. Probe enforces `MACHXO2_MAX_SPEED` and registers the manager.

Control flow: write-init rejects partial reconfiguration, enables ISC, erases, waits for not busy, checks FAIL, and initializes the programming address. Write validates that the bitstream count is a multiple of the 16-byte page size and sends each page with the `LSC_PROGINCRNV` command and delay. Write-complete sends `ISC_PROGRAMDONE`, waits, verifies DONE, then repeatedly refreshes until DONE, no BUSY, and no error or until refresh-loop exhaustion. Cleanup is attempted on failed DONE/refresh checks.

State and persistence: Linux state is the SPI device pointer stored as manager private data. Hardware state includes nonvolatile configuration memory, status bits, error bits, and refresh/programming mode. The loaded image persists according to MachXO2 configuration storage.

Dependencies and integration points: depends on SPI, FPGA manager framework, OF compatible `lattice,machxo2-slave-spi`, and SPI ID `machxo2-slave-spi`.

Risks and test signals: risks include strict 16-byte alignment, limited busy/refresh loop counts, status register endian assumptions, cleanup erasing after failure, and no partial reconfiguration. Test signals are accepted SPI speed, status DONE/ERR transitions, page-count write logs under tracing, manager state operating, and failed malformed payload returning `-EINVAL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/machxo2-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/microchip-spi.c -->
# sources/distributed-fs/ceph-client/drivers/fpga/microchip-spi.c

Purpose: FPGA manager for Microchip PolarFire programming over slave SPI. It parses the Microchip bitstream header to find the actual bitstream and data size, enters ISC/program mode, writes fixed 16-byte frames, and exits program mode.

Important APIs and functions: `struct mpf_priv` stores the SPI device, program-mode flag, and aligned single-byte TX/RX buffers for status commands. `mpf_read_status` performs two status reads and treats SPI violation/error bits as `-EIO`. `mpf_ops_parse_header` discovers lookup-table blocks for component sizes and bitstream start, setting `info->header_size` and `info->data_size`. Manager ops include `mpf_ops_state`, `mpf_ops_write_init`, `mpf_ops_write`, and `mpf_ops_write_complete`.

Control flow: the manager requests an initial 71-byte header and asks the core to skip the parsed header. Header parsing may return `-EAGAIN` to request a larger buffer. Write-init rejects partial reconfiguration, enables ISC with a readback status word, sends frame-init program-mode command, and marks `program_mode`. Write validates 16-byte frame alignment and sends each frame behind an `MPF_SPI_FRAME` command after status polling. Write-complete disables ISC, delays, sends release, and clears `program_mode`.

State and persistence: state is the manager private structure and the hardware status/program mode. Header-derived `info->header_size` and `info->data_size` steer the manager core. The driver does not track a persistent image version; configuration persistence is device-dependent.

Dependencies and integration points: depends on SPI, FPGA manager header parsing support, unaligned little-endian helpers, iopoll, OF compatible `microchip,mpf-spi-fpga-mgr`, and SPI ID `mpf-spi-fpga-mgr`.

Risks and test signals: risks include malformed lookup tables, accumulating `info->data_size` if parse is re-entered without reset, status polling without sleep interval, frame-size strictness, and state reporting unknown whenever status is nonzero. Test signals are parser behavior on short headers, correct header skip/data size, successful ISC enable readback, frame write counts, final release command, and injected SPI violation returning `-EIO`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/microchip-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/of-fpga-region.c -->
# sources/distributed-fs/ceph-client/drivers/fpga/of-fpga-region.c

Purpose: Device Tree support for FPGA regions and overlay-driven FPGA programming. It registers `fpga-region` platform devices, resolves FPGA managers and bridges from DT properties or parent regions, parses overlay image properties, triggers FPGA programming before overlay apply, and releases image/bridge resources after overlay removal.

Important APIs and functions: `of_fpga_region_get_mgr` walks a region and ancestors to find an `fpga-mgr` phandle. `of_fpga_region_get_bridges` adds the parent bridge and `fpga-bridges` phandles from the overlay or region. `of_fpga_region_parse_ov` creates `fpga_image_info` from overlay properties such as `firmware-name`, `partial-fpga-config`, `external-fpga-config`, `encrypted-fpga-config`, and timeout properties. `of_fpga_region_notify` handles overlay pre-apply and post-remove actions. Probe registers an FPGA region and populates child regions.

Control flow: init registers an OF overlay notifier and platform driver. Probe binds DT `fpga-region` nodes to generic region devices. On overlay pre-apply, the notifier finds the target region, rejects child regions that themselves contain `firmware-name`, parses image info, stores it in `region->info`, and calls `fpga_region_program_fpga`. If programming fails, the overlay is rejected and image info is freed. On overlay post-remove, bridges are disabled and put, image info is freed, and `region->info` is cleared.

State and persistence: state includes the notifier, platform driver, each region's manager reference, transient overlay image info, and bridge list references held for the overlay lifetime. Persistent hardware state is the configured FPGA image. DT overlay state controls lifetime of bridge references and image info.

Dependencies and integration points: depends on OF overlay notifications, OF platform population, FPGA manager/bridge/region frameworks, phandle parsing, and platform driver core. It is the main integration between firmware images named in DT overlays and runtime FPGA programming.

Risks and test signals: risks include overlay lifecycle ordering, rejecting nested firmware-name only by matching child regions, ambiguous firmware plus external-config flags, bridge-list cleanup only on post-remove, and manager lookup deferring probe broadly as `-EPROBE_DEFER`. Test signals are `fpga-region` probe logs, overlay pre-apply programming, bridge phandle acquisition, rejected invalid overlays, post-remove bridge put/image free, and timeout flags reaching low-level managers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/of-fpga-region.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/socfpga-a10.c -->
# sources/distributed-fs/ceph-client/drivers/fpga/socfpga-a10.c

Purpose: FPGA manager for Altera/Intel Arria10 SoCFPGA partial reconfiguration. It controls image-configuration registers via regmap, streams data to a dedicated data register, derives clock/data ratio from the RBF header, and checks PR status through image-configuration status bits.

Important APIs and functions: `struct a10_fpga_priv` stores the regmap, data MMIO address, and clock. Register access is constrained by `socfpga_a10_fpga_regmap_config`. Helper functions set configuration width, generate DCLKs, inspect RBF encryption/compression flags, compute CDRATIO, wait for PR ready/done, and read state. Manager ops are `socfpga_a10_fpga_write_init`, `socfpga_a10_fpga_write`, `socfpga_a10_fpga_write_complete`, and `socfpga_a10_fpga_state`.

Control flow: write-init only accepts `FPGA_MGR_PARTIAL_RECONFIG`, validates passive parallel MSEL and external pin status, sets 16-bit configuration width, computes CDRATIO from image header words, enables config control, disables unneeded overrides, generates clocks, asserts PR request, and waits for PR ready. Write streams full and partial 32-bit words to the data register. Write-complete waits for PR done, clears PR request, clocks out cleanup cycles, disables config control, deasserts chip select, disables overrides, and checks usermode/CONDONE/NSTATUS.

State and persistence: state includes enabled clock, regmap, data MMIO, and manager state derived from hardware status. Hardware state includes PR request, chip-select/config overrides, DCLK counters, PR status bits, and partially reconfigured FPGA fabric.

Dependencies and integration points: depends on platform resources for control and data MMIO, clock framework, regmap MMIO, FPGA manager core, OF compatible `altr,socfpga-a10-fpga-mgr`, and RBF header layout.

Risks and test signals: risks include accepting only partial reconfiguration, reading image header offsets as native `u32`, short ten-iteration PR waits without delay, ignored regmap errors in some helpers, and clock lifetime tied to manual unregister. Test signals are clock enable/disable, manager state changes, PR_READY/PR_DONE bits, correct CDRATIO for compressed/encrypted images, successful final usermode check, and errors for invalid MSEL or too-short headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/socfpga-a10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/socfpga.c -->
# sources/distributed-fs/ceph-client/drivers/fpga/socfpga.c

Purpose: FPGA manager for earlier Altera SoCFPGA devices. It resets the FPGA, configures passive-parallel width and CDRATIO from MSEL, writes the bitstream through an FPGA data aperture, waits for CONF_DONE through an interrupt-backed completion, generates final DCLKs, and returns the FPGA to user mode.

Important APIs and functions: `struct socfpga_fpga_priv` stores control/data MMIO, a completion, and IRQ number. Helper functions wrap MMIO, read monitor/status state, clear/generate DCLKs, poll state, configure GPIO-style interrupts, get/set configuration mode, and reset. Manager ops are `socfpga_fpga_ops_configure_init`, `socfpga_fpga_ops_configure_write`, `socfpga_fpga_ops_configure_complete`, and `socfpga_fpga_ops_state`. `socfpga_fpga_isr` completes when CONF_DONE and nSTATUS are asserted.

Control flow: probe maps two resources, gets and requests the IRQ, and registers a devm FPGA manager. Write-init rejects partial reconfiguration, sets mode-specific CDRATIO/width and NCE, enables manager control, asserts and releases reset, waits for configuration state, clears nSTATUS interrupt, and enables AXI config data transfer. Write emits complete and tail 32-bit words. Write-complete waits up to ten milliseconds for interrupt completion, disables AXI config, generates four DCLKs, waits for user mode, and disables manager control.

State and persistence: Linux state is MMIO mappings, IRQ handler, and completion. Hardware state includes control bits, MSEL-derived mode, GPIO monitor/status bits, DCLK counters, and configured FPGA fabric. The bitstream itself persists only as supported by the hardware configuration mode.

Dependencies and integration points: depends on platform resources, OF compatible `altr,socfpga-fpga-mgr`, interrupt core, completions, FPGA manager framework, and SoCFPGA register layout.

Risks and test signals: risks include very short polling timeouts, interrupt-only config-done detection, no support for partial reconfiguration, native-endian word streaming, and potential timeout sensitivity under slow hardware. Test signals are IRQ delivery on CONF_DONE, state sysfs moving to operating, correct reset/config/user-mode transitions, data aperture writes, timeout behavior when nSTATUS fails, and successful devm cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/socfpga.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/stratix10-soc.c -->
# sources/distributed-fs/ceph-client/drivers/fpga/stratix10-soc.c

Purpose: FPGA manager for Intel Stratix10 and Agilex SoC devices where reconfiguration must be performed through a privileged firmware service channel. It requests reconfiguration, allocates service-layer buffers, streams image data through mailbox/service calls, and polls service completion.

Important APIs and functions: `struct s10_priv` stores the service channel, service client, completion, four service buffers, and status bitset. `s10_svc_send_msg` wraps `stratix10_svc_send`. `s10_receive_callback` records service status bits, unlocks returned buffers, and completes waiters. Manager ops are `s10_ops_write_init`, `s10_ops_write`, and `s10_ops_write_complete`. Buffer helpers manage the four `SVC_BUF_SIZE` allocations from the service layer.

Control flow: module init finds a DT `svc` node containing a compatible FPGA manager and populates platform devices before registering the driver. Probe requests the `fpga` service channel and registers the manager. Write-init sends `COMMAND_RECONFIG` with optional partial flag, waits for OK, and allocates four 512 KiB service buffers. Write repeatedly locks a free buffer, copies image data into it, submits `COMMAND_RECONFIG_DATA_SUBMIT`, waits for buffer-submitted or buffer-done statuses, and when no data remains claims/free buffers until all are returned. Write-complete repeatedly sends `COMMAND_RECONFIG_STATUS` until completed, error, or timeout, then calls `stratix10_svc_done`.

State and persistence: state includes the service channel, callback status bitset, completion, and service buffers with bit locks. Hardware state is managed by the privileged firmware service and persisted as FPGA configuration. Buffer ownership is asynchronous and depends on service callbacks returning kernel addresses.

Dependencies and integration points: depends on `stratix10-svc-client`, OF platform population under `svc`, FPGA manager core, completions, and compatible strings `intel,stratix10-soc-fpga-mgr` and `intel,agilex-soc-fpga-mgr`.

Risks and test signals: risks include asynchronous status-bit races, busy-looping on `-ENOBUFS`, buffer-free correctness when errors occur, service timeouts, and no explicit low-level state callback. Test signals are service-channel acquisition, OK response to `COMMAND_RECONFIG`, buffer submitted/done callbacks, all buffers freed after write, completed status from firmware, and clean channel release on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/stratix10-soc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/tests/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/fpga/tests/Kconfig

Purpose: Kconfig entry for FPGA subsystem KUnit tests. It creates `FPGA_KUNIT_TESTS`, allowing the FPGA manager, bridge, and region unit tests to be built when the relevant subsystem dependencies and KUnit are enabled.

Important APIs and control flow: `config FPGA_KUNIT_TESTS` is tristate and is visible unless `KUNIT_ALL_TESTS` selects it implicitly. It depends on `FPGA`, `FPGA_REGION`, `FPGA_BRIDGE`, and `KUNIT=y`; it defaults to `KUNIT_ALL_TESTS`. The help text explains that it builds unit tests for the FPGA subsystem and points readers to KUnit documentation.

State and persistence: this file controls build-time state only. It does not create runtime state, but its selected value determines whether FPGA KUnit test modules/objects are compiled.

Dependencies and integration points: depends on the main FPGA framework symbols and KUnit. It integrates with the local test Makefile through `CONFIG_FPGA_KUNIT_TESTS`.

Risks and test signals: risks include tests being unavailable when KUnit is modular or disabled, dependency drift if new tests require additional framework symbols, and limited visibility when `KUNIT_ALL_TESTS` auto-selects defaults. Test signals are Kconfig dependency resolution, `CONFIG_FPGA_KUNIT_TESTS=y/m`, and successful build/run of `fpga-mgr-test`, `fpga-bridge-test`, and `fpga-region-test`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/tests/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/tests/Makefile -->
# sources/distributed-fs/ceph-client/drivers/fpga/tests/Makefile

Purpose: build mapping for FPGA subsystem KUnit test objects. It connects `CONFIG_FPGA_KUNIT_TESTS` to the manager, bridge, and region KUnit suites.

Important APIs and control flow: the single object rule appends `fpga-mgr-test.o`, `fpga-bridge-test.o`, and `fpga-region-test.o` to `obj-$(CONFIG_FPGA_KUNIT_TESTS)`. Standard kernel build logic compiles these objects when the Kconfig symbol is enabled.

State and persistence: build-time only. It creates no runtime state, but determines which KUnit test object files are linked into the kernel or module set.

Dependencies and integration points: depends on `drivers/fpga/tests/Kconfig` selecting `CONFIG_FPGA_KUNIT_TESTS` and on the corresponding test source files in the same directory. It integrates with Kbuild and the FPGA subsystem's test coverage.

Risks and test signals: risks include stale object names if tests are renamed or split and no per-test granularity in Kconfig. Test signals are successful Kbuild resolution, generated test objects, and KUnit execution reporting manager, bridge, and region suite results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/tests/Makefile -->
