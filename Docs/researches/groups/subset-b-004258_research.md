# sources/distributed-fs/ceph-client/drivers/misc subset-b-004258 research

Grouped research for `subset-b-004258`. Each section is wrapped with the exact source-path markers expected by the reconciliation lane and is written to stand alone when split into `Docs/researches/<source>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ibmvmc.c -->
# sources/distributed-fs/ceph-client/drivers/misc/ibmvmc.c

## Purpose
`ibmvmc.c` implements the IBM Power Systems Virtual Management Channel misc driver. It exposes `/dev/ibmvmc` for a management application and binds a VIO device compatible with `ibm,vmc`. The driver negotiates VMC capabilities with the hypervisor through a CRQ, allocates DMA buffers per HMC session, and copies message payloads between user space and hypervisor-owned remote I/O windows with `H_COPY_RDMA`.

## Important APIs, types, and functions
The file operations are `ibmvmc_open`, `ibmvmc_close`, `ibmvmc_read`, `ibmvmc_write`, `ibmvmc_poll`, and `ibmvmc_ioctl`. Supported ioctls are `VMC_IOCTL_SETHMCID`, `VMC_IOCTL_QUERY`, and `VMC_IOCTL_REQUESTVMC`. Hypervisor-facing helpers wrap `H_COPY_RDMA`, `H_FREE_CRQ`, `H_REQUEST_VMC`, `H_REG_CRQ`, and `H_SEND_CRQ`. CRQ flow is handled by `ibmvmc_handle_event`, `ibmvmc_task`, `crq_queue_next_crq`, `ibmvmc_handle_crq`, `ibmvmc_handle_crq_init`, and `ibmvmc_crq_process`. Buffer/session helpers include `ibmvmc_add_buffer`, `ibmvmc_rem_buffer`, `ibmvmc_recv_msg`, `ibmvmc_send_msg`, `ibmvmc_send_open`, `ibmvmc_send_close`, `ibmvmc_setup_hmc`, and `ibmvmc_return_hmc`.

## Control flow
Module init registers the miscdevice, initializes global HMC slots, sanitizes module parameters, and registers the VIO driver. VIO probe reads local and remote DMA window numbers, starts a reset kthread, initializes/registers the CRQ, enables interrupts, and sends an initialization CRQ. CRQ init messages trigger a response followed by `VMC_MSG_CAP`; a valid `VMC_MSG_CAP_RESP` moves the global state to ready and clamps MTU, pool size, and HMC count. A user opens the miscdevice, calls `SETHMCID` to reserve an HMC and send `VMC_MSG_OPEN`, then reads and writes HMC protocol payloads. Incoming `VMC_MSG_SIGNAL` performs RDMA from the hypervisor window into a local DMA buffer and queues the buffer for blocking or polled reads. Writes copy from user space into a locally owned buffer, RDMA it to the hypervisor window, and signal the buffer id and length through CRQ.

## State and persistence
State is in static globals: `ibmvmc`, `hmcs[]`, `ibmvmc_adapter`, module parameters, and `ibmvmc_read_wait`. Persistent kernel-visible state lasts only while the module is loaded and the VIO device is bound. Per-HMC state tracks session number, open state, buffer metadata, a circular queue of inbound message buffer ids, and the owning file session. Reset paths close all HMCs, wake blocked readers when appropriate, free DMA buffers, and either await partner CRQ init or schedule CRQ re-registration in process context.

## Dependencies and integration points
The driver depends on PowerPC pseries VIO, PAPR hypercalls, DMA mapping APIs, tasklets, wait queues, kthreads, miscdevice infrastructure, and user-copy helpers. It integrates with user space through `/dev/ibmvmc` and with the hypervisor through CRQ and remote DMA windows described in VIO device-tree attributes.

## Risks
The global singleton design assumes one VMC adapter. Queue head/tail wrap only logs overflow, so sustained inbound traffic could overwrite unread queue state. Some helper paths call buffer selection while already holding the same HMC spinlock, which is worth auditing for lock nesting behavior. `ibmvmc_recv_msg` trusts negotiated `msg_len` sufficiently for RDMA but should remain constrained by negotiated MTU. Reset races with close/read/write are mitigated by state checks and wakeups but remain the highest behavioral risk.

## Test signals
Useful validation signals are successful miscdevice registration, VIO probe messages, CRQ init/capability exchange reaching `ibmvmc_state_ready`, `VMC_IOCTL_QUERY` returning a VMC state and DRC index, successful `SETHMCID` open response, blocking read wakeups after `VMC_MSG_SIGNAL`, and clean reset/reprobe behavior. Fault tests should cover invalid HMC indexes, invalid buffer ids, copy-to/from-user failures, partner reset (`valid == 0xff`), and module parameter clamping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ibmvmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ibmvmc.h -->
# sources/distributed-fs/ceph-client/drivers/misc/ibmvmc.h

## Purpose
`ibmvmc.h` defines the public and internal contract for the IBM VMC driver. It contains protocol constants, ioctl numbers, message opcodes/status codes, global and per-HMC state enums, CRQ message layouts, DMA-buffer descriptors, and session/container structures shared by `ibmvmc.c`.

## Important APIs, types, and functions
The user ABI constants are `VMC_IOCTL_SETHMCID`, `VMC_IOCTL_QUERY`, and `VMC_IOCTL_REQUESTVMC`; `struct ibmvmc_query_struct` is copied to user space. The wire format is represented by `struct ibmvmc_admin_crq_msg` for capability exchange and `struct ibmvmc_crq_msg` for ordinary VMC commands. Driver structures include `struct ibmvmc_buffer`, `struct crq_queue`, `struct crq_server_adapter`, `struct ibmvmc_struct`, `struct ibmvmc_hmc`, and `struct ibmvmc_file_session`.

## Control flow
The header itself has no executable flow, but it encodes the state transitions implemented in the C file. `enum ibmvmc_states` progresses from initial to CRQ init, capabilities, ready, failed, with a negative scheduled-reset state. `enum ibmhmc_states` progresses from free to initial, opening, ready, or failed. Message opcodes describe the request/response sequence: capability exchange, open/close, add/remove buffer, and signal messages.

## State and persistence
`struct ibmvmc_buffer` tracks whether each DMA buffer is valid, free, local or hypervisor owned, its id, size, message length, local/remote DMA addresses, and local virtual address. `struct ibmvmc_hmc` persists each HMC session's state, id string, buffer pool, queue, and attached file session. `struct ibmvmc_struct` carries global negotiated values and VMC DRC index.

## Dependencies and integration points
The header depends on Linux types, `cdev`, and PowerPC `asm/vio.h`. Endian-annotated fields (`__be16`, `__be32`) are part of the CRQ ABI and must match hypervisor expectations exactly. The ioctl constants form the user/kernel ABI for management applications.

## Risks
Changing structure layout, opcode values, endian annotations, ioctl numbers, or limits is ABI-sensitive. `MAX_HMCS` and `MAX_BUF_POOL_SIZE` are compile-time array limits, while negotiated values are runtime clamps; callers must never index by module parameters without validating against negotiated maximums.

## Test signals
Build validation should confirm this header compiles on the intended PowerPC VIO configurations. ABI tests should verify ioctl numbers and struct sizes remain stable, and runtime tests should confirm capability negotiation honors the declared min, max, and default limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ibmvmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ics932s401.c -->
# sources/distributed-fs/ceph-client/drivers/misc/ics932s401.c

## Purpose
`ics932s401.c` is an I2C hardware-monitor style driver for the Integrated Circuits ICS932S401 clock generator. It exposes read-only sysfs attributes for spread spectrum state, CPU/SRC/PCI clock selections and calculated frequencies, USB/reference clocks, and spread percentages.

## Important APIs, types, and functions
The driver registers an `i2c_driver` in `I2C_CLASS_HWMON`, scans address `0x69`, and implements `.detect`, `.probe`, and `.remove`. `struct ics932s401_data` stores a mutex, cached register bytes, and cache freshness timestamps. Important helpers are `ics932s401_update_device`, `calculate_cpu_freq`, `calculate_src_freq`, `calculate_pci_freq`, and the `show_*` sysfs callbacks.

## Control flow
Detection verifies SMBus byte-data support, reads the vendor/revision and device registers as words, shifts the mirrored byte out of the high byte, and reports type `ics932s401`. Probe allocates state, initializes the mutex, and creates a sysfs group. Sysfs reads call `ics932s401_update_device`, which refreshes the selected mirrored registers at most every two seconds and then derives output values from cached register fields. Remove drops the sysfs group and frees state.

## State and persistence
The only persistent state is per-client cached register data. It is read-only from this driver perspective; the driver does not program clock registers. Cache state is protected by `data->lock`, and stale or failed reads are converted to zero in the cache refresh path.

## Dependencies and integration points
The driver depends on Linux I2C/SMBus, sysfs, jiffies timing, mutexes, and hwmon class scanning. DMI module aliases target IBM IntelliStation and System x platforms that use this clock chip.

## Risks
Frequency calculations depend on register interpretation and divisor tables; wrong mirrored-byte handling would report bad clocks. Failed register reads becoming zero can hide I2C errors behind plausible but incorrect sysfs values. The use of `BUG()` in generic show helpers would be unsafe if attribute wiring were changed incorrectly.

## Test signals
Signals include successful auto-detection at `0x69`, sysfs group creation, stable `*_clock` and `*_clock_selection` values across cache intervals, correct spread percentage formatting, and removal without stale sysfs files. Fault tests should exercise absent chip, unsupported SMBus functionality, and I2C read failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ics932s401.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/isl29003.c -->
# sources/distributed-fs/ceph-client/drivers/misc/isl29003.c

## Purpose
`isl29003.c` implements an I2C driver for the Intersil ISL29003 ambient light sensor. It exposes legacy sysfs controls for range, resolution, mode, power state, and computed lux.

## Important APIs, types, and functions
`struct isl29003_data` stores the I2C client, a mutex, a cache of four writable/control registers, and the pre-suspend power state. Register helpers `__isl29003_read_reg` and `__isl29003_write_reg` operate on masked fields and keep the cache synchronized after successful writes. Sensor helpers include `isl29003_get/set_range`, `isl29003_get/set_resolution`, `isl29003_get/set_mode`, `isl29003_get/set_power_state`, and `isl29003_get_adc_value`. Probe/remove and sleep PM hooks are registered through `module_i2c_driver`.

## Control flow
Probe checks SMBus byte support, allocates state, fills the register cache from hardware, writes default range/resolution/mode/power-off configuration, and creates the sysfs attribute group. Sysfs stores parse decimal values and constrain them to the bit-field range before writing. `lux` first checks power state, then reads LSB/MSB sensor registers under the mutex, combines the raw value, and scales by selected gain range and bit depth. Suspend stores current power state and powers down; resume rewrites cached registers and restores the prior power state.

## State and persistence
The register cache is the authoritative view for sysfs reads of configuration fields and is replayed on resume. The sensor's measured lux value is not persisted; it is read on demand. The driver powers the sensor off during initialization, removal, and suspend unless the previous power state is restored on resume.

## Dependencies and integration points
The driver depends on I2C SMBus byte transfers, sysfs, mutexes, simple PM ops, and the legacy misc-device documentation ABI for ISL29003. It integrates through I2C device IDs only; there is no OF/ACPI match table in this file.

## Risks
`isl29003_get_power_state` interprets the cached command register, so external register writes would desynchronize sysfs state. The low-level read helper does not validate `reg` bounds, although current callers use cachable registers. Lux conversion depends on range/resolution fields being valid and on power state being enabled by user space.

## Test signals
Probe should fail cleanly when any initial register read fails. Sysfs tests should verify boundary rejection for range/resolution/mode/power, lux returning `-EBUSY` while powered off, expected scaling at all four gain ranges and resolutions, and suspend/resume replaying cached configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/isl29003.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/isl29020.c -->
# sources/distributed-fs/ceph-client/drivers/misc/isl29020.c

## Purpose
`isl29020.c` is a compact I2C ambient light sensor driver for the Intersil ISL29020. It creates an `isl29020` sysfs group with `lux0_sensor_range` and `lux0_input`.

## Important APIs, types, and functions
The driver registers an `i2c_driver` named `isl29020`. Sysfs callbacks are `als_sensing_range_show`, `als_sensing_range_store`, and `als_lux_input_data_show`. `als_set_default_config` initializes register `0x00` to `0xc0`, and `als_set_power_state` toggles the enable bit in register `0x00`. Runtime PM callbacks power the chip off/on.

## Control flow
Probe writes default config, creates the sysfs group, powers the chip off, and enables runtime PM. Range reads decode the low two bits of register `0x00` into `1000`, `4000`, `16000`, or `64000`. Range writes clamp user input to the smallest supported range that can contain it and update the register. Lux reads runtime-resume the device, wait 100 ms, read MSB and LSB under a global mutex, read the range bits, runtime-suspend, and calculate lux from the 16-bit ADC value.

## State and persistence
There is no private per-device allocation. State lives in sensor registers and the PM core; a file-scope mutex serializes data-register reads across all devices. Runtime PM state determines whether the sensor is powered between sysfs accesses.

## Dependencies and integration points
The file depends on I2C SMBus byte transfers, sysfs, runtime PM, and kernel delay APIs. It integrates through the I2C device id `isl29020` and a named sysfs subgroup.

## Risks
Using a global mutex rather than per-client locking is conservative but may unnecessarily serialize multiple sensors. Some error paths call `pm_runtime_put_sync` before unlocking or after partial reads; the ordering is simple but should be regression-tested. There is no explicit functionality check in probe, so unsupported adapters fail through SMBus operations. The range register can be changed outside the driver and no cache exists.

## Test signals
Probe should show the default config write and sysfs group creation. Tests should read/write all range thresholds, validate lux scaling for known ADC values, confirm runtime suspend disables the sensor and runtime resume enables it, and verify sysfs removal on device detach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/isl29020.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/keba/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/misc/keba/Kconfig

## Purpose
This Kconfig fragment exposes KEBA CP500 system FPGA support and the KEBA LAN9252 configuration helper.

## Important APIs, types, and functions
`CONFIG_KEBA_CP500` is a tristate option for the PCI system FPGA driver. It depends on `X86_64 || ARM64 || COMPILE_TEST`, `PCI`, and `I2C`, and selects `AUXILIARY_BUS`. `CONFIG_KEBA_LAN9252` is a tristate option for the SPI LAN9252 configuration driver. It depends on `SPI` and either `KEBA_CP500` or `COMPILE_TEST`.

## Control flow
The file participates in kernel configuration only. Selecting CP500 enables compilation of the PCI parent that registers auxiliary subdevices. Selecting LAN9252 enables the SPI child driver used when the CP500 EEPROM indicates a LAN9252 EtherCAT slave controller.

## State and persistence
No runtime state is stored here. The selected configuration controls whether `cp500.o` and `lan9252.o` can be built as built-ins or modules.

## Dependencies and integration points
The dependency graph mirrors runtime integration: CP500 needs PCI and I2C/nvmem-discovered EEPROMs, and LAN9252 needs an SPI master plus either the CP500 platform or compile-test coverage.

## Risks
Incorrect dependencies would allow builds without required subsystem symbols or hide valid hardware support. `AUXILIARY_BUS` selection is required because `cp500.c` publishes child devices using auxiliary-device APIs.

## Test signals
Kconfig tests should cover built-in, module, disabled, and `COMPILE_TEST` combinations on x86_64 and arm64. Build output should produce `cp500.ko` and/or `lan9252.ko` under the expected option names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/keba/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/keba/Makefile -->
# sources/distributed-fs/ceph-client/drivers/misc/keba/Makefile

## Purpose
The Makefile maps KEBA Kconfig options to object files.

## Important APIs, types, and functions
`obj-$(CONFIG_KEBA_CP500) += cp500.o` builds the CP500 PCI system FPGA driver. `obj-$(CONFIG_KEBA_LAN9252) += lan9252.o` builds the LAN9252 SPI configuration driver.

## Control flow
Kbuild evaluates the two `obj-*` assignments during the kernel build. Depending on each tristate value, the object is omitted, built into the kernel, or built into a module.

## State and persistence
No runtime state exists. The build artifact state is fully controlled by Kconfig.

## Dependencies and integration points
The file integrates the KEBA subdirectory with the surrounding `drivers/misc` Kbuild hierarchy and relies on Kconfig to enforce subsystem dependencies.

## Risks
The main risk is object/Kconfig drift: renaming a config option or source file without updating this file would silently drop driver builds.

## Test signals
Build tests should verify that enabling `CONFIG_KEBA_CP500=m` produces `cp500.ko`, enabling `CONFIG_KEBA_LAN9252=m` produces `lan9252.ko`, and built-in configurations link both objects without missing symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/keba/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/keba/cp500.c -->
# sources/distributed-fs/ceph-client/drivers/misc/keba/cp500.c

## Purpose
`cp500.c` is the PCI parent driver for KEBA CP500 family system FPGAs. The FPGA contains multiple IP cores; this driver maps family-specific register windows, exposes version and reconfiguration sysfs attributes, registers auxiliary devices for I2C/SPI/fan/battery/UART children, and creates logical nvmem devices over the CPU EEPROM.

## Important APIs, types, and functions
Key structures are `struct cp500_dev_info`, `struct cp500_devs`, `struct cp500_nvmem`, and `struct cp500`. PCI entry points are `cp500_probe` and `cp500_remove`. Child registration helpers are `cp500_register_i2c`, `cp500_register_spi`, `cp500_register_fan`, `cp500_register_batt`, `cp500_register_uart`, and `cp500_register_auxiliary_devs`. NVMEM flow uses `cp500_nvmem`, `cp500_nvmem_match`, `cp500_nvmem_register`, and `cp500_nvmem_unregister`. Sysfs is implemented by `version_show` and `keep_cfg_show/store`.

## Control flow
Probe allocates `struct cp500`, records BAR bases, selects one of three device maps by PCI device ID, enables PCI bus mastering, maps the startup register area, allocates MSI-X vectors, reads the FPGA version register, registers an nvmem notifier, installs an AXI error IRQ when present, and registers immediate auxiliary devices. I2C is registered first and publishes board info for temperature sensor and EEPROMs. When the CPU EEPROM's nvmem provider appears, the notifier creates `cpu_eeprom` and `user_eeprom` nvmem slices, reads the device assembly byte to decide the EtherCAT slave controller type, and registers SPI children including LAN9252 only when appropriate. Remove unregisters nvmem, auxiliary children, IRQs, MSI-X vectors, and disables PCI.

## State and persistence
Runtime state is per PCI device in `struct cp500`. Persistent hardware state includes FPGA startup/reconfiguration bits and EEPROM contents. The `keep_cfg` sysfs attribute writes the reconfiguration request bit; this affects the next reset/reboot rather than immediate runtime behavior. Atomic `nvmem_notified` ensures the EEPROM-driven setup runs once.

## Dependencies and integration points
The driver depends on PCI, MSI-X, auxiliary bus, nvmem provider/consumer APIs, I2C board-info instantiation, SPI flash platform data, MTD partitions, and KEBA auxiliary device types from `linux/misc/keba.h`. It is a parent for separate KEBA child drivers and for standard EEPROM, SPI flash, temperature, and UART-related drivers.

## Risks
Child registration is partly asynchronous via nvmem, so ordering bugs can leave SPI unregistered or base nvmem references leaked. Family-specific offsets must match FPGA layouts. `cp500_spi_info` is static and modified for CP035 flash data, so multi-device systems with mixed families deserve scrutiny. Error handling logs child registration failures and continues, which favors partial functionality but can hide missing subdevices.

## Test signals
Hardware or emulation tests should confirm PCI IDs bind, version strings are correct, `keep_cfg` toggles the startup register, MSI-X allocation paths work with and without AXI/MMI vectors, auxiliary devices appear with correct resources, EEPROM nvmem slices are readable, and LAN9252 SPI registration follows the EEPROM ESC-type bit. Removal should unregister children before parent resources disappear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/keba/cp500.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/keba/lan9252.c -->
# sources/distributed-fs/ceph-client/drivers/misc/keba/lan9252.c

## Purpose
`lan9252.c` configures the LAN9252 EtherCAT slave controller on KEBA CP500 devices over SPI/PDI. Its specific job is to ensure the PHY is fixed to 100 Mbps full duplex with autonegotiation disabled.

## Important APIs, types, and functions
The SPI wire commands are represented by packed `struct lan9252_read_cmd` and `struct lan9252_write_cmd`. Low-level helpers are `lan9252_spi_read` and `lan9252_spi_write`. ESC CSR access flows through `lan9252_esc_wait`, `lan9252_esc_read`, and `lan9252_esc_write`. MII management is controlled by `lan9252_access_mii`, `lan9252_mii_wait`, `lan9252_mii_read`, and `lan9252_mii_write`. `lan9252_probe` performs initialization and configuration.

## Control flow
Probe retries `lan9252_init` up to ten times, checking the byte-test register and hardware-ready bit. It grants PDI access to MII management, reads BMCR for PHY address 2, and if the PHY is not already full duplex, 100 Mbps, and autonegotiation-disabled, rewrites BMCR. It then returns MII management access to EtherCAT regardless of success on the main path.

## State and persistence
The driver stores no private state. It changes LAN9252 ESC and PHY registers directly. The PHY configuration persists in the controller until reset or rewritten by another controller owner.

## Dependencies and integration points
The driver depends on SPI, MII bit definitions, and the CP500 SPI child device registration that instantiates modalias `lan9252`. It uses EtherCAT CSR indirection registers rather than memory mapping.

## Risks
SPI read/write endianness and packed command layout must match the controller protocol. Timeouts are short (`100us` CSR, `500us` MII), so slow hardware could fail probe. The final `lan9252_access_mii(false)` return value is ignored, so a failed hand-back to EtherCAT would only be visible indirectly. There is no remove callback because configuration is one-shot.

## Test signals
Probe logs should show successful initialization and PHY configuration. Tests should cover byte-test mismatch, hardware-not-ready, CSR busy timeout, MII error bits, BMCR already-correct path, BMCR rewrite path, and restoration of MII access after errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/keba/lan9252.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/kgdbts.c -->
# sources/distributed-fs/ceph-client/drivers/misc/kgdbts.c

## Purpose
`kgdbts.c` is the in-kernel KGDB test suite. It registers a fake `kgdb_io` transport that emulates GDB remote protocol packets to validate software breakpoints, hardware breakpoints, single stepping, bad memory reads, optional NMI behavior, and breakpoint stress on `kernel_clone` or `do_sys_openat2`.

## Important APIs, types, and functions
Test scripting uses `struct test_struct` and `struct test_state`. Packet generation/validation uses `fill_get_buf`, `run_simple_test`, and `validate_simple_test`. Breakpoint helpers include `sw_break`, `hw_break`, removal variants, write/access hardware break helpers, `check_and_rewind_pc`, and `check_single_step`. Top-level runners are `kgdbts_run_tests`, `configure_kgdbts`, and `init_kgdbts`. KGDB integration is through `kgdbts_io_ops`, `kgdb_register_io_module`, `kgdb_unregister_io_module`, `kgdb_breakpoint`, and module parameter `kgdbts`.

## Control flow
Configuration arrives from the `kgdbts=` boot option or sysfs module parameter. `configure_kgdbts` optionally runs an early plant/detach sanity test, registers the fake I/O module, and starts `kgdbts_run_tests`. Each test is a table of expected get/put packets. During KGDB exceptions, `read_char` feeds scripted packets to KGDB, while `write_char` accumulates KGDB responses, validates them, advances the table index, and schedules ACKs. Optional long-running clone/open tests spawn a thread that unregisters the I/O module after a final ACK.

## State and persistence
The suite is stateful through file-scope buffers, counters, config string, breakpoint target addresses, thread ids, single-step emulation state, and a configured flag. It has no persistent storage; state lasts until tests complete or the module parameter is changed. It intentionally manipulates kgdb global debugger state and module references during exception entry/exit.

## Dependencies and integration points
The file depends on KGDB internals, kallsyms lookup, architecture register conversion helpers, breakpoint instruction size definitions, NMI watchdog touching, kthreads, and syscall symbol names. Architecture quirks are handled for emulated single-step and adjusted breakpoint offsets.

## Risks
This code intentionally triggers breakpoints and debugger paths, so it can hang or destabilize a system when KGDB or architecture support is broken. Symbol-name drift (`do_sys_openat2`, `kernel_clone`) affects optional tests. The packet tables rely on GDB remote protocol details. The static lookup cache is intentionally non-reentrant because debug traps stop other CPUs.

## Test signals
Expected signals are `kgdbts:RUN` messages, lack of `ERROR PUT` validation failures, successful unregister after final ACK, and no memory change after plant/detach. Coverage should include boot-time `kgdbts=V1 kgdbwait`, runtime sysfs invocation, hardware breakpoint capable and incapable architectures, single-step emulation architectures, and optional `F`, `S`, `I`, and `N` modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/kgdbts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/lan966x_pci.c -->
# sources/distributed-fs/ceph-client/drivers/misc/lan966x_pci.c

## Purpose
`lan966x_pci.c` is a PCI wrapper for Microchip LAN966x devices. It requires an OF node for the PCI device, creates a one-interrupt IRQ domain, applies an embedded DT overlay, and populates platform children from that overlay.

## Important APIs, types, and functions
`struct pci_dev_intr_ctrl` owns the PCI device, irq domain, and allocated IRQ. IRQ-domain flow uses `pci_dev_irq_domain_map`, `pci_dev_irq_domain_ops`, `pci_dev_irq_handler`, `pci_dev_create_intr_ctrl`, and managed wrapper `devm_pci_dev_create_intr_ctrl`. Overlay flow uses `lan966x_pci_load_overlay`, `lan966x_pci_unload_overlay`, `of_overlay_fdt_apply`, `of_overlay_remove`, and `of_platform_default_populate`. PCI entry points are `lan966x_pci_probe` and `lan966x_pci_remove`.

## Control flow
Probe first rejects devices without `dev_of_node`, because the overlay needs an OF target. It enables the PCI device with pcim, creates an IRQ domain backed by INTx, allocates driver data, applies the embedded `lan966x_pci` DTBO, enables bus mastering, and populates platform devices below the OF node. Remove depopulates platform children and removes the overlay; managed cleanup removes the IRQ controller.

## State and persistence
Per-device state is `struct lan966x_pci`, mainly the overlay changeset id. The IRQ controller state is managed by devres. Overlay-applied OF nodes persist only while the PCI driver remains bound.

## Dependencies and integration points
The driver depends on PCI dynamic OF nodes, OF overlays, OF platform population, IRQ domains, and embedded DTBO symbols generated by the kernel build. It binds PCI vendor `PCI_VENDOR_ID_EFAR` device `0x9660`.

## Risks
Probe fails on ACPI systems unless the PCI core has created a valid OF node. Overlay apply/remove ordering is critical: child platform devices must be depopulated before overlay removal. IRQ disposal uses mapping `0`; leaks or stale mappings would affect child IRQ consumers.

## Test signals
Tests should verify binding with dynamic OF nodes, successful overlay application, child platform-device creation, INTx interrupt translation through the irq domain, and clean remove/reprobe cycles. Failure tests should cover missing OF node, IRQ allocation failure, overlay apply failure, and child population failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/lan966x_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/lattice-ecp3-config.c -->
# sources/distributed-fs/ceph-client/drivers/misc/lattice-ecp3-config.c

## Purpose
`lattice-ecp3-config.c` configures supported Lattice ECP3 FPGAs over SPI using the firmware file `lattice-ecp3.bit`. It identifies the FPGA, clears configuration memory, streams the bitstream, disables writing, and checks the DONE bit.

## Important APIs, types, and functions
`struct fpga_data` carries a completion used to wait for asynchronous firmware loading on remove. `struct ecp3_dev` lists supported reversed JTAG IDs. `firmware_load` contains the full configuration sequence. `lattice_ecp3_probe` allocates state and calls `request_firmware_nowait`; `lattice_ecp3_remove` waits for completion.

## Control flow
Probe requests firmware asynchronously and returns after registration. The callback rejects missing or zero-length firmware, sends READ_ID, validates the JEDEC ID, reads status, allocates a transmit buffer with WRITE_INC header plus firmware data, sends REFRESH, WRITE_EN, and CLEAR, polls status up to five seconds for the CLEARED value, writes the bitstream, sends WRITE_DIS, rereads status, reports whether DONE is set, releases firmware, frees the buffer, and completes `fw_loaded`.

## State and persistence
Driver state is minimal and devm-managed. Hardware state changes are persistent in the FPGA configuration until power cycle or reconfiguration. The completion protects remove from racing the asynchronous callback.

## Dependencies and integration points
The driver depends on SPI transfers, request_firmware, unaligned big-endian helpers, and module firmware loading. It binds SPI IDs `ecp3-17` and `ecp3-35`.

## Risks
SPI transfer return values are mostly not checked in the callback, so bus errors could be reported only as failed status/DONE checks. The status comparison for CLEARED expects an exact value, which may be brittle if other status bits are set. Asynchronous firmware loading means remove ordering relies on completion.

## Test signals
Validation should cover firmware missing, zero-size firmware, unsupported JEDEC ID, clear timeout, successful DONE set, DONE not set, and remove during firmware load. SPI traces should show the expected command ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/lattice-ecp3-config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/lis3lv02d/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/misc/lis3lv02d/Kconfig

## Purpose
This Kconfig fragment exposes bus-specific ST LIS3LV02Dx accelerometer drivers for SPI and I2C.

## Important APIs, types, and functions
`CONFIG_SENSORS_LIS3_SPI` builds the SPI transport and selects the shared `SENSORS_LIS3LV02D` core. It depends on `!ACPI`, `SPI_MASTER`, and `INPUT`. `CONFIG_SENSORS_LIS3_I2C` builds the I2C transport, depends on `I2C` and `INPUT`, and also selects the shared core.

## Control flow
The file only controls build configuration. Selecting either bus driver pulls in the common accelerometer core that provides sysfs, input, misc freefall, and shared sensor logic.

## State and persistence
No runtime state exists. The tristate choices determine whether `lis3lv02d.o`, `lis3lv02d_spi.o`, and/or `lis3lv02d_i2c.o` are built in or as modules.

## Dependencies and integration points
The options reflect runtime integration with SPI/I2C bus subsystems and the input subsystem. The SPI driver excludes ACPI, while the I2C path can be used with platform data or OF.

## Risks
Incorrect dependencies could build transport code without input or bus symbols. Because both transports select the same singleton core, configurations enabling both should be considered carefully in runtime tests.

## Test signals
Build matrix tests should validate SPI-only, I2C-only, both-as-modules, and both-built-in configurations. Help text should match module names `lis3lv02d`, `lis3lv02d_spi`, and `lis3lv02d_i2c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/lis3lv02d/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/lis3lv02d/Makefile -->
# sources/distributed-fs/ceph-client/drivers/misc/lis3lv02d/Makefile

## Purpose
The Makefile connects LIS3 accelerometer Kconfig options to Kbuild objects.

## Important APIs, types, and functions
`obj-$(CONFIG_SENSORS_LIS3LV02D) += lis3lv02d.o` builds the shared core. `obj-$(CONFIG_SENSORS_LIS3_SPI) += lis3lv02d_spi.o` builds SPI glue. `obj-$(CONFIG_SENSORS_LIS3_I2C) += lis3lv02d_i2c.o` builds I2C glue.

## Control flow
Kbuild includes the core when selected by either transport and includes each transport object according to its tristate value.

## State and persistence
No runtime state exists. Build output determines which module or built-in objects provide the common exported symbols and bus drivers.

## Dependencies and integration points
The Makefile relies on Kconfig to select `SENSORS_LIS3LV02D` when a transport is enabled, ensuring the transport modules can resolve common symbols such as `lis3lv02d_init_device`.

## Risks
Object ordering and option names must stay aligned with exported symbols and transport module names. A missing core object would break transport linking.

## Test signals
Build tests should confirm `lis3lv02d.ko`, `lis3lv02d_spi.ko`, and `lis3lv02d_i2c.ko` are produced under module configurations and link correctly under built-in configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/lis3lv02d/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/lis3lv02d/lis3lv02d.c -->
# sources/distributed-fs/ceph-client/drivers/misc/lis3lv02d/lis3lv02d.c

## Purpose
`lis3lv02d.c` is the shared core for ST LIS3-family accelerometers. It abstracts bus operations behind function pointers, detects sensor type, provides sysfs attributes, exposes an input polled joystick device, optionally registers `/dev/freefall`, handles IRQ/click/freefall events, manages runtime PM power transitions, and parses OF/platform configuration.

## Important APIs, types, and functions
The exported singleton is `struct lis3lv02d lis3_dev`. Exported functions are `lis3lv02d_init_device`, `lis3lv02d_joystick_enable`, `lis3lv02d_joystick_disable`, `lis3lv02d_poweroff`, `lis3lv02d_poweron`, `lis3lv02d_remove_fs`, and `lis3lv02d_init_dt`. Important internals include `lis3lv02d_get_xyz`, `lis3lv02d_set_odr`, `lis3lv02d_selftest`, `lis3_context_save/restore`, interrupt handlers, miscdevice file operations, and sysfs callbacks for `selftest`, `position`, and `rate`.

## Control flow
Transport probe fills bus callbacks and calls `lis3lv02d_init_device`. The core reads `WHO_AM_I`, selects precision/rate/scale/read-data tables, allocates register cache, creates a faux sysfs device, powers on the chip, enables runtime PM, registers an input device, applies platform/OF interrupt and click/wakeup settings, requests IRQs when available, and registers `/dev/freefall`. Data reads use block read when available or per-axis reads, scale raw values, and apply axis remapping. Sysfs access briefly runtime-resumes the device and schedules delayed suspend. Remove paths disable joystick/freefall, destroy sysfs, power off if needed, disable runtime PM, and free cache.

## State and persistence
Core state lives in the global `lis3_dev`, including bus callbacks, register cache, platform data, input/misc devices, IRQ state, wait queue, async queue, axis mapping, ODR tables, and wake-thread counters. Register context is saved before regulator poweroff and restored after poweron when a transport supplies `reg_ctrl`. OF platform data is dynamically allocated and stored in `lis3->pdata`.

## Dependencies and integration points
The core depends on input polling, faux devices, miscdevice, runtime PM, IRQ threading, regulators via transports, OF parsing, wait queues, fasync, and `linux/lis3lv02d.h` platform-data definitions. It is consumed by both I2C and SPI glue.

## Risks
The singleton design limits safe multi-device support. I2C read helpers used by transports may return success even when the byte value is negative-truncated, so error propagation depends on callback correctness. Power/sysfs/runtime-PM interactions are subtle because sysfs visitors schedule delayed suspend while input and misc opens hold runtime PM references. Interrupt behavior varies sharply by sensor type and platform data.

## Test signals
Tests should cover all supported `WHO_AM_I` variants, axis remap module parameter validation, sysfs position/rate/selftest, input registration and polling, freefall misc read/poll/fasync, click key events, IRQ-driven data-ready selftest counts, runtime suspend/resume register restoration, OF property parsing, and remove while sysfs delayed suspend is pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/lis3lv02d/lis3lv02d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/lis3lv02d/lis3lv02d.h -->
# sources/distributed-fs/ceph-client/drivers/misc/lis3lv02d/lis3lv02d.h

## Purpose
`lis3lv02d.h` defines the shared internal interface for LIS3-family accelerometer core and bus glue. It lists register addresses, chip IDs, control/status bit definitions, axis conversion, and the central `struct lis3lv02d`.

## Important APIs, types, and functions
Important enums include `lis3_reg`, `lis302d_reg`, `lis3lv02d_reg`, `lis3_who_am_i`, sensor type identifiers, control-register bit sets, status bits, freefall/wakeup bits, click bits, and regulator states. `union axis_conversion` maps hardware axes to logical axes. `struct lis3lv02d` carries bus callbacks, ODR tables, register cache, input/faux/misc devices, regulators, IRQ state, platform data, mutex, and optional OF node. Function prototypes expose the core to bus transports, and `extern struct lis3lv02d lis3_dev` declares the singleton.

## Control flow
The header provides no executable flow but defines how transports call into the core: they fill `init`, `read`, `write`, optional `blkread`, optional `reg_ctrl`, bus private data, IRQ, axis conversion, platform data, and PM device before calling `lis3lv02d_init_device`.

## State and persistence
The state schema includes hardware register context (`regs`, `reg_cache`, `regs_stored`), runtime sensor parameters (`whoami`, `scale`, `odrs`, `odr_mask`, `shift_adj`), OS integration objects (`idev`, `fdev`, `miscdev`), and interrupt counters. This state persists for the lifetime of the bound transport device.

## Dependencies and integration points
The header depends on faux devices, input, regulators, miscdevice, and public platform data from `linux/lis3lv02d.h`. It is included by the shared core plus I2C/SPI transport files.

## Risks
Register and bit definitions are ABI-like for hardware; incorrect values break multiple transports. The singleton declaration encodes the driver's single-device assumption. Adding a new sensor variant requires consistent updates to IDs, control bits, data-reading behavior, and core initialization.

## Test signals
Build coverage should include both transports and OF/platform-data configurations. Runtime tests should confirm each register definition used by initialization, IRQ configuration, and sysfs/selftest paths matches the target sensor datasheet.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/lis3lv02d/lis3lv02d.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/lis3lv02d/lis3lv02d_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/misc/lis3lv02d/lis3lv02d_i2c.c

## Purpose
`lis3lv02d_i2c.c` is the I2C transport for the LIS3 accelerometer core. It supplies SMBus read/write/block-read callbacks, regulator control, OF/platform-data setup, IRQ and PM integration, and calls the common core initializer.

## Important APIs, types, and functions
Transport callbacks are `lis3_i2c_write`, `lis3_i2c_read`, `lis3_i2c_blockread`, `lis3_i2c_init`, and `lis3_reg_ctrl`. Driver entry points are `lis3lv02d_i2c_probe` and `lis3lv02d_i2c_remove`. PM callbacks are `lis3lv02d_i2c_suspend`, `lis3lv02d_i2c_resume`, `lis3_i2c_runtime_suspend`, and `lis3_i2c_runtime_resume`. The OF match table recognizes `st,lis3lv02d`.

## Control flow
Probe optionally parses OF into core platform data, applies platform-data axis maps and block-read feature selection, calls platform resource setup, obtains `Vdd` and `Vdd_IO` regulators, fills the global `lis3_dev`, powers regulators for initialization, calls `lis3lv02d_init_device`, and turns regulators back off so runtime PM owns later power. Remove releases platform resources, disables joystick, removes core sysfs, and frees regulators. System sleep keeps wakeup-configured devices powered as needed, while runtime PM calls common poweroff/poweron.

## State and persistence
The file stores no per-client allocation of its own; it mutates global `lis3_dev`. Regulator descriptors are kept in that global. Platform resource setup may create board-specific state outside this file and is released through platform callbacks.

## Dependencies and integration points
The driver depends on I2C SMBus byte and optional I2C block functionality, regulator bulk APIs, runtime/system PM, OF matching, platform data, and the shared LIS3 core. It publishes I2C IDs `lis3lv02d` and `lis331dlh`.

## Risks
`lis3_i2c_read` assigns a possibly negative SMBus return to `u8` and returns 0, which can mask read errors. The global `lis3_dev` means two I2C devices conflict. Regulator state is toggled around core init and again by runtime PM, so failed init paths must keep regulator cleanup correct. OF-allocated platform data is not explicitly freed in this transport path.

## Test signals
Tests should verify probe with and without platform data, OF parsing, block read selection only when adapter supports it, regulator enable/disable sequencing, IRQ propagation from `client->irq`, runtime PM transitions, system sleep wakeup behavior, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/lis3lv02d/lis3lv02d_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/lis3lv02d/lis3lv02d_spi.c -->
# sources/distributed-fs/ceph-client/drivers/misc/lis3lv02d/lis3lv02d_spi.c

## Purpose
`lis3lv02d_spi.c` is the SPI glue layer for LIS302DL/LIS3 accelerometers. It configures SPI mode, provides byte read/write callbacks, passes IRQ/platform data to the shared core, and handles suspend/resume power transitions.

## Important APIs, types, and functions
Callbacks are `lis3_spi_read`, `lis3_spi_write`, and `lis3_spi_init`. Driver entry points are `lis302dl_spi_probe` and `lis302dl_spi_remove`. PM callbacks are `lis3lv02d_spi_suspend` and `lis3lv02d_spi_resume`. OF match supports `st,lis302dl-spi`.

## Control flow
Probe forces 8-bit words and SPI mode 0, calls `spi_setup`, fills the global `lis3_dev` with SPI callbacks, IRQ, normal axis mapping, and platform data, optionally parses OF data, stores driver data, and calls `lis3lv02d_init_device`. Remove disables joystick/freefall, powers off the sensor, and removes core sysfs. Suspend powers off unless platform wakeup flags require the sensor to remain armed; resume powers back on under the same condition.

## State and persistence
This transport stores its bus pointer and configuration in the global `lis3_dev`; it has no private allocation. Hardware register state is managed by the common core.

## Dependencies and integration points
The driver depends on SPI core helpers (`spi_w8r8`, `spi_write`, `spi_setup`), PM sleep ops, optional OF matching, platform data, and the shared LIS3 core.

## Risks
There is no block-read callback, so SPI reads use the slower per-register core path. The singleton core again prevents safe multi-device binding. Probe unconditionally changes `spi->mode`, which may surprise board descriptions if a variant needs a different mode. `lis3_spi_read` maps any negative SPI result to `-EINVAL`, losing the specific error code.

## Test signals
Tests should verify SPI setup parameters, read/write command bytes with the read bit, successful core initialization, IRQ/freefall behavior, OF parsing, suspend/resume with and without wakeup flags, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/lis3lv02d/lis3lv02d_spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/lkdtm/Makefile -->
# sources/distributed-fs/ceph-client/drivers/misc/lkdtm/Makefile

## Purpose
The LKDTM Makefile builds the Linux Kernel Dump Test Module object set and applies special build rules needed for specific tests.

## Important APIs, types, and functions
`obj-$(CONFIG_LKDTM) += lkdtm.o` creates the composite module. Component objects include `core.o`, `bugs.o`, `heap.o`, `perms.o`, `refcount.o`, `rodata_objcopy.o`, `usercopy.o`, `kstack_erase.o`, `cfi.o`, `fortify.o`, and optional `powerpc.o`. Special flags disable KASAN for `stackleak.o`, remove LTO/rethunk/CFI flags from `rodata.o`, and use objcopy to rename `.noinstr.text` into `.rodata` for rodata tests.

## Control flow
Kbuild assembles `lkdtm.o` from the listed objects when LKDTM is enabled. The custom target builds `rodata_objcopy.o` from `rodata.o` through `if_changed,objcopy`.

## State and persistence
No runtime state exists. Build-time state controls whether LKDTM tests are instrumented or deliberately uninstrumented in ways required by the test cases.

## Dependencies and integration points
The file integrates LKDTM with Kbuild, compiler instrumentation flags, objcopy, and architecture-specific optional sources. It ensures CFI and rodata tests can exercise intended mitigation boundaries.

## Risks
Incorrect instrumentation flags can invalidate LKDTM results: tests may fail to trigger or be blocked by unrelated compiler transformations. Missing component objects would hide crash types from `core.o` registration.

## Test signals
Build tests should verify LKDTM links with `CONFIG_LKDTM`, the objcopy rule runs, `rodata_objcopy.o` has the expected section rename, and CFI/LTO flag removal is reflected in compile commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/lkdtm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/lkdtm/bugs.c -->
# sources/distributed-fs/ceph-client/drivers/misc/lkdtm/bugs.c

## Purpose
`lkdtm/bugs.c` registers LKDTM crash types that exercise generic logic bugs and hardening features: panics, BUG/WARN, exceptions, lockups, stack exhaustion/corruption/reporting, unaligned access, integer overflow, bounds checking, list hardening, VMAP stack guard pages, SMEP pinning, x86 double fault, and arm64 PAC corruption.

## Important APIs, types, and functions
Initialization uses `lkdtm_bugs_init` for recursion depth. Each `lkdtm_*` function implements a crash type listed in the `crashtypes` array and exported through `bugs_crashtypes`. Notable helpers are `recursive_loop`, hrtimer callbacks for hardirq panic/BUG, stop-machine panic helper, stack canary scanner, SMP call lockup helper, and list corruption simulations.

## Control flow
LKDTM core invokes selected crash functions by name. Many functions intentionally never return or deliberately crash. Others perform a within-bounds operation first, then an out-of-bounds or corrupted operation to verify a mitigation traps. At the end, each crash type is registered with `CRASHTYPE(...)` entries and a category descriptor.

## State and persistence
File-scope state tracks recursion depth, a spinlock intentionally left locked, warning count, panic/BUG wait flags, stack offset/canary observations, and volatile integer values used to prevent compiler optimization. State persists within the module and can affect repeated tests, such as `SPINLOCKUP` requiring two invocations.

## Dependencies and integration points
The file depends on LKDTM core macros, scheduler/task stack APIs, stop_machine, hrtimers, list APIs, slab allocation, uaccess, CPU hotplug read locks, architecture-specific x86 and arm64 helpers, UBSAN/list/stack hardening configs, and mitigation reporting helpers such as `pr_expected_config`.

## Risks
Every crash type is intentionally dangerous. Some tests leave the system hung or unstable if the intended mitigation is absent. Architecture-specific code must be guarded correctly. Compiler optimizations are actively resisted with `volatile`, `noinline`, explicit memory clearing, and special build flags elsewhere.

## Test signals
Expected signals are architecture/config-dependent crashes or `XFAIL`/`FAIL` messages. Coverage should include list hardening, UBSAN bounds, counted-by support, pointer member bounds, stack protector, VMAP stack, lockup detectors, SMEP pinning on x86_64, double fault on x86_32, and PAC corruption on arm64.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/lkdtm/bugs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/lkdtm/cfi.c -->
# sources/distributed-fs/ceph-client/drivers/misc/lkdtm/cfi.c

## Purpose
`lkdtm/cfi.c` provides LKDTM crash types for forward-edge and backward-edge control-flow integrity. It checks whether mismatched indirect-call prototypes are blocked and whether stack return-address tampering is stopped by PAC or shadow call stack.

## Important APIs, types, and functions
Forward-edge testing uses `lkdtm_increment_void`, `lkdtm_increment_int`, `lkdtm_indirect_call`, and `lkdtm_CFI_FORWARD_PROTO`. Backward-edge testing uses `set_return_addr_unchecked`, `set_return_addr`, architecture-specific `FRAME_RA_OFFSET`, `no_pac_addr`, and `lkdtm_CFI_BACKWARD`. The `crashtypes` array exports `CFI_FORWARD_PROTO` and `CFI_BACKWARD` through `cfi_crashtypes`.

## Control flow
`CFI_FORWARD_PROTO` first performs a valid indirect call, then casts an incompatible function pointer and calls it through the same indirect-call helper. With CFI enabled, the mismatched call should trap before the final failure message. `CFI_BACKWARD` first demonstrates that an unprotected helper can rewrite the return address, then tries the same through a normal helper and expects PAC or shadow call stack to preserve control flow.

## State and persistence
`called_count` records indirect-call side effects, and `force_check` prevents compiler simplification while making label addresses reachable. No state is persistent beyond module lifetime.

## Dependencies and integration points
The file depends on LKDTM core registration, compiler CFI instrumentation, arm64 pointer authentication/BTI/SCS attributes, RISC-V frame layout differences, `__builtin_frame_address`, labels-as-values, and page-offset masking for PAC-stripped comparisons.

## Risks
The return-address tests depend on compiler frame layout and architecture calling conventions. If the helper cannot find the return address, the test warns instead of proving mitigation behavior. Special attributes intentionally disable PAC/SCS for the unchecked helper, so build-flag drift can invalidate the test.

## Test signals
A protected kernel should trap or report expected mitigation behavior before `FAIL` messages. Useful configurations include `CONFIG_CFI`, `CONFIG_ARM64_PTR_AUTH_KERNEL`, `CONFIG_SHADOW_CALL_STACK`, and builds without those mitigations to verify warning/XFAIL behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/lkdtm/cfi.c -->
