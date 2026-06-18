# subset-b-004246 research

This grouped report covers the requested Linux MFD, PMIC, USB-host, and MCU core drivers. Each section is wrapped with the required source-path markers for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/omap-usb-host.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/omap-usb-host.c

## Purpose
`omap-usb-host.c` is the parent USBHS host-controller driver for TI OMAP EHCI/OHCI blocks. It owns the common UHH register programming, revision-dependent port-mode setup, runtime clock handling, and creation of EHCI/OHCI child devices.

## Important APIs, Types, And Functions
`struct usbhs_hcd_omap` stores per-port clocks, OMAP revision, UHH base, and `usbhs_omap_platform_data`. `omap_usbhs_alloc_child()` and `omap_usbhs_alloc_children()` create legacy platform children. `usbhs_runtime_resume()` and `usbhs_runtime_suspend()` gate TLL and per-port clocks. `omap_usbhs_init()`, `omap_usbhs_rev1_hostconfig()`, and `omap_usbhs_rev2_hostconfig()` program `OMAP_UHH_HOSTCONFIG`. `usbhs_omap_get_dt_pdata()` maps DT `portN-mode` strings into platform-data enums.

## Control Flow
Probe builds platform data from DT when needed, maps the UHH resource, initializes TLL, enables runtime PM long enough to read `OMAP_UHH_REVISION`, derives the port count, acquires revision-specific clocks, selects UTMI clock parents for OMAP4+ PHY/TLL modes, writes HOSTCONFIG, and then either populates DT child nodes or allocates legacy `ehci-omap` and `ohci-omap3` children. Remove disables runtime PM and depopulates/unregisters children.

## State And Persistence
Driver state is in devm-managed memory and volatile hardware registers. Runtime PM transitions persist only while the device is active. Child devices receive copied platform data and a 32-bit DMA mask.

## Dependencies And Integration Points
It depends on platform resources named `ehci`, `ehci-irq`, `ohci`, and `ohci-irq`, OMAP USB platform data, the paired TLL exports in `omap-usb.h`, DT compatibles `ti,usbhs-host`, `ti,ehci-omap`, and `ti,ohci-omap3`, clock framework APIs, and EHCI/OHCI child drivers.

## Risks
Probe calls `omap_tll_init()` but does not check its return, so init ordering relies on `fs_initcall` sequencing. OMAP4+ clock lookup treats missing per-port clocks as fatal despite comments suggesting optional behavior. Port-mode and revision logic directly changes HOSTCONFIG bit fields, so DT mistakes can disable ports or select the wrong PHY/TLL/HSIC mode. Runtime PM clock enable errors are logged but not propagated.

## Test Signals
Useful tests include DT and legacy platform boots, OMAP3 and OMAP4+ revision paths, all PHY/TLL/HSIC port combinations, runtime suspend/resume balance, child-device creation and removal, USB enumeration through EHCI/OHCI, and failure injection for missing clocks/resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/omap-usb-host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/omap-usb-tll.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/omap-usb-tll.c

## Purpose
`omap-usb-tll.c` drives the OMAP USB TLL block used by OMAP EHCI/OHCI ports in TLL, OHCI FS/LS, and HSIC modes. It exposes helper functions consumed by the USBHS host parent to initialize, enable, and disable TLL channels.

## Important APIs, Types, And Functions
`struct usbtll_omap` holds the TLL MMIO base, channel count, and channel clocks. Exported APIs are `omap_tll_init()`, `omap_tll_enable()`, and `omap_tll_disable()`. Helpers include `ohci_omap3_fslsmode()` for OHCI port-mode conversion and `omap_usb_mode_needs_tll()` for per-port clock decisions.

## Control Flow
Probe maps the TLL register resource, enables runtime PM, reads `OMAP_USBTLL_REVISION` to choose two or three channels, allocates flexible clock storage, prepares `usb_tll_hs_usb_chN_clk` clocks, drops runtime PM, and publishes a global `tll_dev` under `tll_lock`. `omap_tll_init()` programs shared TLL configuration and per-channel mode bits based on USBHS platform data. Enable and disable gate per-channel clocks around host runtime PM.

## State And Persistence
The driver uses a global `tll_dev` pointer protected by a spinlock, devm-managed device state, prepared clocks, and volatile TLL channel registers. Register state is reprogrammed by `omap_tll_init()` and clock state follows runtime PM users.

## Dependencies And Integration Points
It integrates with `omap-usb-host.c` through `omap-usb.h`, with platform data from `<linux/platform_data/usb-omap.h>`, DT compatible `ti,usbhs-tll`, clock framework, MMIO accessors, and runtime PM.

## Risks
The exported helpers return `-ENODEV` when called before probe, but the host driver ignores the init return. The helpers use a spinlock while dereferencing device state and touching registers/clocks; changes must preserve sleepability constraints. Channel count is revision-derived and port-mode arrays must be large enough for all channels. The HSIC path relies on UTMI-style configuration bits.

## Test Signals
Exercise probe before host init, all known TLL revisions, TLL-free PHY-only setups, OHCI FS/LS modes, EHCI TLL and HSIC modes, runtime PM reference balance, channel clock failure handling, and remove while host children are gone.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/omap-usb-tll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/omap-usb.h -->
# sources/distributed-fs/ceph-client/drivers/mfd/omap-usb.h

## Purpose
`omap-usb.h` is the local bridge header between the OMAP USBHS host parent and the OMAP USB TLL driver.

## Important APIs, Types, And Functions
It declares `omap_tll_init(struct usbhs_omap_platform_data *pdata)`, `omap_tll_enable(struct usbhs_omap_platform_data *pdata)`, and `omap_tll_disable(struct usbhs_omap_platform_data *pdata)`.

## Control Flow
There is no executable flow. The declarations define the call sequence expected by the host driver: initialize channel registers during host probe, enable TLL clocks on host runtime resume, and disable them on runtime suspend.

## State And Persistence
No state is stored in the header. State lives in `omap-usb-tll.c` and in platform data supplied by `omap-usb-host.c`.

## Dependencies And Integration Points
The API depends on `struct usbhs_omap_platform_data` from the OMAP USB platform-data header. It is included by both OMAP USB MFD source files and is the only local compile-time contract between them.

## Risks
The header does not encode ownership, locking, or return-value requirements. Callers must know that TLL probe publishes global state and that helpers may fail with `-ENODEV`.

## Test Signals
Build coverage across both source files, successful symbol export/linking, and boot tests where TLL is initialized before USBHS host probe are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/omap-usb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/palmas.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/palmas.c

## Purpose
`palmas.c` is the TI Palmas/TWL603x/TPS659xx family I2C MFD core. It creates multiple I2C clients/regmaps, configures interrupt handling, decodes pad mux state for child GPIO/PWM/LED users, writes PMU power-control policy, and populates DT children.

## Important APIs, Types, And Functions
`palmas_regmap_config[]` defines three client register windows. `palmas_irq_chip` and `tps65917_irq_chip` describe variant-specific regmap IRQ layouts. `palmas_ext_control_req_config()` is exported for regulator/resource consumers to assign external request lines. `palmas_dt_to_pdata()`, `palmas_set_pdata_irq_flag()`, `palmas_power_off()`, and `palmas_i2c_probe()` drive setup. `struct palmas_driver_data` selects features and IRQ chip.

## Control Flow
Probe obtains platform data or derives it from DT, allocates `struct palmas`, creates dummy I2C clients for secondary addresses, attaches regmaps, optionally configures IRQ polarity and clear-on-read behavior, registers a regmap IRQ chip, writes or reads pad mux registers, derives GPIO/PWM/LED mux masks, writes `PALMAS_POWER_CTRL`, populates DT children, and optionally registers `pm_power_off`. Remove tears down IRQs, dummy clients, and global poweroff state.

## State And Persistence
Persistent hardware state includes pad mux registers, interrupt polarity/clear behavior, external request assignments, power-control masks, and DEV_ON poweroff writes. Driver state stores regmaps, dummy clients, mux masks, IRQ data, feature flags, and a global `palmas_dev` for poweroff.

## Dependencies And Integration Points
It depends on I2C, regmap, regmap-irq, MFD core, OF child population, `linux/mfd/palmas.h`, IRQ trigger metadata, and DT properties such as `ti,mux-pad1`, `ti,mux-pad2`, `ti,power-ctrl`, `ti,system-power-controller`, and `ti,palmas-override-powerhold`.

## Risks
Global `pm_power_off` ownership is single-device and must be cleared on remove. Dummy client creation and of-node references must remain balanced. IRQ cleanup is called even when IRQ setup may have been skipped, so changes around no-IRQ paths need care. Pad mux interpretation is bitfield-heavy and drives child behavior. External request configuration silently ignores invalid IDs or missing `PALMAS_EXT_REQ`.

## Test Signals
Boot supported compatibles (`ti,palmas`, `ti,tps659038`, `ti,tps65917`), verify child devices, regmap IRQ delivery, IRQ polarity from DT/firmware, pad mux masks, exported external request control, system poweroff behavior, no-IRQ probe, and dummy-client error cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/palmas.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/pf1550.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/pf1550.c

## Purpose
`pf1550.c` is the NXP PF1550 PMIC core. It verifies the chip, reads OTP configuration for regulator DVS support, builds nested interrupt domains for top-level, regulator, onkey, and charger interrupts, and registers the corresponding MFD children.

## Important APIs, Types, And Functions
`pf1550_regmap_config` defines the 8-bit I2C regmap. `pf1550_irq_chip`, `pf1550_regulator_irq_chip`, `pf1550_onkey_irq_chip`, and `pf1550_charger_irq_chip` describe hierarchical regmap IRQ controllers. `pf1550_read_otp()` unlocks and reads OTP bytes. `pf1550_i2c_probe()` is the main setup function, with `pf1550_suspend()` and `pf1550_resume()` managing wake IRQ behavior.

## Control Flow
Probe allocates private data, initializes regmap, reads and validates `PF1550_PMIC_REG_DEVICE_ID`, reads OTP words for SW2/SW3 and SW1/SW2 DVS enable bits, registers the top-level IRQ chip on the physical IRQ, obtains virtual IRQs for regulator/onkey/charger categories, registers each nested IRQ chip on its parent vIRQ, then adds one MFD child per function with the nested domain.

## State And Persistence
State is devm-managed and includes regmap, IRQ chip data, physical IRQ, and boolean DVS capability flags for child regulators. Hardware state is affected by OTP-key writes and interrupt mask/ack setup. No nonvolatile data is written.

## Dependencies And Integration Points
It depends on I2C, regmap, regmap-irq, MFD core, `linux/mfd/pf1550.h`, OF compatible `nxp,pf1550`, and child drivers named `pf1550-regulator`, `pf1550-onkey`, and `pf1550-charger`.

## Risks
The driver assumes a valid IRQ; `devm_regmap_add_irq_chip()` is called with `pf1550->irq` without a no-IRQ fallback. Nested IRQ setup is order-sensitive, and resource IRQ numbers must match the regmap IRQ domains passed to `devm_mfd_add_devices()`. OTP unlock writes touch privileged registers and must not be rearranged casually.

## Test Signals
Validate device ID rejection, OTP DVS flag decoding, top-level category interrupts, nested regulator/onkey/charger IRQ delivery, wakeup suspend/resume, missing or shared IRQ behavior, and child driver resource lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/pf1550.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/qcom-pm8008.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/qcom-pm8008.c

## Purpose
`qcom-pm8008.c` is the Qualcomm PM8008 I2C MFD core. It claims the PMIC's two I2C addresses, provides primary and secondary regmaps, configures a per-peripheral regmap IRQ chip, and registers regulator, temperature alarm, and GPIO children.

## Important APIs, Types, And Functions
`pm8008_irqs[]` maps misc, temp-alarm, and GPIO interrupts. `pm8008_get_irq_reg()` converts logical regmap-irq offsets into peripheral-based addresses. `pm8008_set_type_config()` programs edge/level and polarity configuration buffers. `pm8008_irq_chip` defines main status, mask/unmask, ack, config, and register addressing. `pm8008_probe()` wires the full device.

## Control Flow
Probe creates a dummy client at `addr + 1`, initializes and attaches the secondary regmap, initializes the primary regmap last as the default, optionally drives reset GPIO low, waits briefly, creates a named IRQ-domain fwnode, registers the regmap IRQ chip on the physical IRQ, stores the IRQ domain for the GPIO child, and adds `pm8008-regulator`, `qpnp-temp-alarm`, and `pm8008-gpio` MFD children.

## State And Persistence
State is devm-managed: dummy I2C client, two regmaps, IRQ fwnode, regmap IRQ data, reset GPIO descriptor, and child devices. Hardware state includes interrupt mask, ack, and type/polarity registers. There is no persistent storage outside the PMIC registers.

## Dependencies And Integration Points
It depends on I2C, regmap, regmap-irq fwnodes, GPIO descriptors, MFD core, IRQ domains, OF compatible `qcom,pm8008`, and child drivers using the regmap and IRQ domain.

## Risks
The secondary regmap is initialized with `qcom_mfd_regmap_cfg` and then attached with `pm8008_regmap_cfg_2`; ordering is intentional because the default regmap must be attached last. IRQ register address calculation depends on `PM8008_NUM_PERIPHS` and the base table staying aligned. The reset GPIO is requested as `GPIOD_OUT_LOW`, so board polarity must match bindings.

## Test Signals
Probe with both I2C addresses present, regmap name visibility, interrupt type programming for temp/GPIO edge and level modes, temp alarm resource IRQ, GPIO child access to the stored IRQ domain, reset-GPIO boards, and cleanup of allocated fwnodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/qcom-pm8008.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/qcom-pm8xxx.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/qcom-pm8xxx.c

## Purpose
`qcom-pm8xxx.c` is the core/IRQ controller for older Qualcomm PM8xxx SSBI PMICs. It creates an SSBI-backed regmap, exposes a linear IRQ domain, handles PM8058/PM8921-style and PM8821-style interrupt topologies, and populates child devices.

## Important APIs, Types, And Functions
`struct pm_irq_chip` holds regmap, spinlock, IRQ domain, topology counts, variant data, and per-hwirq config bytes. `pm8xxx_irq_handler()` walks root/master/block status registers. `pm8821_irq_handler()` handles PM8821's two-master layout. IRQ chip callbacks include mask/ack, unmask, set_type, and get line-level state. `pm8xxx_probe()` initializes regmap, revision logging, IRQ domain, physical IRQ, wake, and children.

## Control Flow
Probe selects `pm_irq_data` by compatible, gets the parent IRQ, initializes SSBI regmap using `ssbi_reg_read/write`, reads two hardware revision registers, allocates `pm_irq_chip`, creates a fwnode-backed linear IRQ domain, requests the physical IRQ with the variant handler, marks it wake-capable, and calls `of_platform_populate()`. Runtime IRQ handling reads root status, selects blocks, reads bit status, and dispatches nested hwirqs through `generic_handle_domain_irq()`.

## State And Persistence
State includes the regmap, spinlock, IRQ domain, and cached per-IRQ configuration. Hardware interrupt configuration is persistent until rewritten. Child devices are DT-populated under the PMIC node.

## Dependencies And Integration Points
It depends on SSBI, regmap custom bus callbacks, IRQ domains, chained/nested IRQ infrastructure, OF population, compatibles `qcom,pm8058`, `qcom,pm8821`, and `qcom,pm8921`, plus child nodes that consume two-cell IRQ specifiers.

## Risks
The PM8821 unmask path uses `regmap_update_bits(..., BIT(irq_bit), ~BIT(irq_bit))`, which relies on regmap masking semantics and is easy to misread. IRQ type programming only exists for PM8xxx, not PM8821. Block/master arithmetic differs by variant. Error paths after IRQ-domain creation rely on remove or explicit cleanup. Spinlocked SSBI block select and status/config reads must stay serialized.

## Test Signals
Validate revision reads, interrupt dispatch for every master/block, two-cell IRQ translation, edge/level type programming, line-level reads, PM8821-specific topology, wake from PMIC IRQ, child node population, and IRQ-domain removal on probe failure/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/qcom-pm8xxx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/qcom-spmi-pmic.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/qcom-spmi-pmic.c

## Purpose
`qcom-spmi-pmic.c` is the common Qualcomm SPMI PMIC parent. It creates an SPMI regmap, loads or inherits PMIC revision identity across multi-USID PMICs, exports `qcom_pmic_get()` for child drivers, and populates PMIC child devices.

## Important APIs, Types, And Functions
`struct qcom_spmi_dev` stores USID count and `struct qcom_spmi_pmic` revision data. `qcom_pmic_get_base_usid()` locates the base SPMI device for a multi-USID PMIC. `pmic_spmi_load_revid()` reads type, subtype, revision, major/minor, optional FAB ID, and applies legacy revision quirks. `pmic_spmi_get_base_revid()` copies base revision data under `pmic_spmi_revid_lock`. `qcom_pmic_get()` is exported.

## Control Flow
Probe initializes an extended SPMI regmap and context. If the current USID is a base USID, it reads revision registers; otherwise it finds the sibling base USID and defers until that device is bound. It stores drvdata under a mutex, then calls `devm_of_platform_populate()`. Remove clears drvdata under the same mutex.

## State And Persistence
State is per-SPMI-device drvdata plus revision metadata copied from hardware. The mutex protects cross-device lookups during probe/remove. The driver does not alter persistent PMIC configuration.

## Dependencies And Integration Points
It depends on the SPMI core, `devm_regmap_init_spmi_ext()`, OF matching for many Qualcomm PMIC compatibles, `soc/qcom/qcom-spmi-pmic.h`, and child drivers that call `qcom_pmic_get()` for subtype/revision decisions.

## Risks
Sibling discovery supports only one- and two-USID PMICs. Probe ordering can defer non-base USIDs. `qcom_pmic_get()` assumes the parent matches and has valid drvdata; child drivers should handle error pointers or probe deferral. Type mismatch returns the read result, which may be zero, leaving unsupported hardware identification subtle.

## Test Signals
Exercise one-USID and two-USID PMIC DT layouts, non-base probing before base probing, revision quirks for PM8941/PM8226/PM8110, FAB ID reads for PMI8998/PM660, child `qcom_pmic_get()` calls, and remove while children are unbinding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/qcom-spmi-pmic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/qcom_rpm.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/qcom_rpm.c

## Purpose
`qcom_rpm.c` is the Qualcomm Resource Power Manager parent for older platforms. It maps RPM message RAM, validates firmware version, exports synchronous resource-write transactions, handles RPM ack/error/wakeup interrupts, and populates child devices such as regulators and clocks.

## Important APIs, Types, And Functions
`struct qcom_rpm_resource` maps logical resource IDs to target/status/select registers and payload size. `struct qcom_rpm_data` captures SoC-specific resource tables and request/ack register offsets. `struct qcom_rpm` holds MMIO bases, IPC syscon, completion, lock, and variant data. `qcom_rpm_write()` is exported for child consumers. IRQ handlers are `qcom_rpm_ack_interrupt()`, `qcom_rpm_err_interrupt()`, and `qcom_rpm_wakeup_interrupt()`.

## Control Flow
Probe enables the optional RAM clock, obtains named IRQs, maps status/control/request windows, reads the `qcom,ipc` syscon phandle/offset/bit, validates the firmware version against match data, mirrors version into control registers, requests IRQs, marks ack and wakeup IRQs wake-capable, and populates children. `qcom_rpm_write()` serializes callers, writes payload words, selects the resource bit, writes request context, rings IPC, waits for ack completion, and reports timeout or RPM rejection.

## State And Persistence
Resource writes alter RPM-managed hardware state outside Linux, such as regulator, clock, fabric, and switch votes. Driver state includes a mutex-protected transaction path and latest `ack_status`. Request/ack select registers are explicitly cleared on ack.

## Dependencies And Integration Points
It depends on DT compatibles for APQ8064/MSM8660/MSM8960/IPQ806x/MDM9615, `dt-bindings/mfd/qcom-rpm.h`, syscon/regmap IPC, MMIO resources, named interrupts, optional `ram` clock, and children that use the exported `qcom_rpm_write()` API.

## Risks
`qcom_rpm_write()` validates exact payload size and resource index with `WARN_ON`, so child tables must match firmware. Only one transaction is allowed at a time. Ack timeout is five seconds and may stall callers. Fatal error IRQ only re-rings IPC and logs. Resource tables are large hand-maintained ABI maps and off-by-one select IDs can affect unrelated RPM resources.

## Test Signals
Probe each SoC template, firmware version mismatch handling, successful regulator/clock votes, rejected request reporting, timeout behavior, ack select clearing, wakeup IRQ behavior, optional RAM-clock absence, and child population under the RPM node.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/qcom_rpm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/qnap-mcu.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/qnap-mcu.c

## Purpose
`qnap-mcu.c` is the serdev MFD core for QNAP NAS microcontrollers connected over UART. It implements the command/reply protocol, exposes exported command helpers, reads firmware version, registers a poweroff handler, and adds EEPROM, input, LED, and hwmon child devices.

## Important APIs, Types, And Functions
`struct qnap_mcu_reply` tracks a single expected reply buffer, length, bytes received, and completion. `struct qnap_mcu` holds serdev, bus lock, reply state, variant data, and version. `qnap_mcu_exec()` and `qnap_mcu_exec_with_ack()` are exported to children. `qnap_mcu_csum()`, `qnap_mcu_verify_checksum()`, `qnap_mcu_receive_buf()`, `qnap_mcu_get_version()`, and `qnap_mcu_power_off()` implement protocol and lifecycle.

## Control Flow
Probe allocates state, selects variant data, initializes lock/completion, opens serdev, sets baud/flow/parity, reads MCU version with `%V`, registers a `SYS_OFF_MODE_POWER_OFF_PREPARE` handler, copies variant platform data into each MFD cell, and adds child devices. Commands are serialized by `bus_lock`; transmit appends XOR checksum, receive accumulates the exact expected length or early error response, completion wakes the caller, and checksum/error codes are validated before copying payload.

## State And Persistence
Runtime state is one in-flight reply and a firmware version cache. Persistent behavior is the MCU's external state: drive power, LEDs, fan, EEPROM, and poweroff command effects. Variant data includes baud rate, drive count, fan PWM range, and USB LED support.

## Dependencies And Integration Points
It depends on serdev, MFD core, reboot/sys-off APIs, `linux/mfd/qnap-mcu.h`, compatibles `qnap,ts133-mcu`, `qnap,ts233-mcu`, and `qnap,ts433-mcu`, plus child drivers named `qnap-mcu-eeprom`, `qnap-mcu-input`, `qnap-mcu-leds`, and `qnap-mcu-hwmon`.

## Risks
Only one command can be active; unsolicited data is discarded with a warning. Error replies are shorter than normal replies and depend on early detection. `memcpy(reply_data, rx, reply_data_size)` copies the requested payload size even if an error-sized reply reached completion, but errors are checked before copy. Global cell platform-data mutation in probe assumes one active variant at a time or identical static cell reuse semantics.

## Test Signals
Protocol tests for checksum, split receive, generic/checksum error replies, timeouts, ACK validation, version command, poweroff command, all variants, child command serialization, and unsolicited UART bytes are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/qnap-mcu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/rave-sp.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/rave-sp.c

## Purpose
`rave-sp.c` is the serdev MFD core for Zodiac Inflight Innovations RAVE supervisory processor MCUs. It implements framed UART transport, command translation, checksum variants, synchronous command execution, event ACK/notifier delivery, firmware status discovery, and DT child population.

## Important APIs, Types, And Functions
Protocol state is in `struct rave_sp_deframer`, `struct rave_sp_reply`, `struct rave_sp_checksum`, and `struct rave_sp`. Exported APIs are `rave_sp_exec()` and `devm_rave_sp_register_event_notifier()`. Framing helpers include `stuff()`, `rave_sp_write()`, `rave_sp_receive_buf()`, and `rave_sp_receive_frame()`. Variant hooks live in `struct rave_sp_variant_cmds` with legacy, RDU1, and RDU2 implementations.

## Control Flow
Probe reads `current-speed`, opens serdev, configures UART, selects variant data, initializes locks/notifier head, queries status or version commands, logs firmware/bootloader strings, and populates DT children. `rave_sp_exec()` translates a generic command, assigns an atomic ACK ID, installs expected reply under `reply_lock`, writes a stuffed frame with checksum, and waits up to one second. Receive deframes STX/DLE/ETX byte streams, verifies checksum, distinguishes events from replies, ACKs events, and notifies registered consumers.

## State And Persistence
State includes deframer progress, atomic ACK ID, one protected pending reply, notifier list, and firmware string allocations. MCU state is external and command-dependent. No on-disk persistence exists.

## Dependencies And Integration Points
It depends on serdev, OF child population, `linux/mfd/rave-sp.h`, CRC-ITU-T, unaligned helpers, blocking notifiers, and child devices under compatibles `zii,rave-sp-niu`, `zii,rave-sp-mezz`, `zii,rave-sp-esb`, `zii,rave-sp-rdu1`, and `zii,rave-sp-rdu2`.

## Risks
The deframer intentionally drops a frame when a second STX appears before ETX and returns partial consumption, so receive-path changes must respect serdev reentry. `rave_sp_exec()` does not check the return value of `rave_sp_write()`. Reply matching requires code, ACK ID, and minimum payload length; unexpected frames are ignored until timeout. Variant command maps are protocol ABI and easy to break.

## Test Signals
Test byte-stuffing, bad/short/oversized frames, CCITT and 8-bit checksums, command timeout, mismatched ACK IDs, event notification and ACK frames, all variant command translations, firmware status fallback, and concurrent child notifier registration/removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/rave-sp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/rc5t583-irq.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/rc5t583-irq.c

## Purpose
`rc5t583-irq.c` is the custom nested IRQ controller for the Ricoh RC5T583 PMIC. It maps PMIC interrupt groups to Linux IRQs, caches mask/edge registers, handles the threaded parent IRQ, clears PMIC status, and dispatches enabled child IRQs.

## Important APIs, Types, And Functions
`struct rc5t583_irq_data` maps each logical IRQ to interrupt type, master bit, group index, enable bit, and mask register index. `rc5t583_irq_mask()`, `rc5t583_irq_unmask()`, `rc5t583_irq_set_type()`, `rc5t583_irq_sync_unlock()`, and `rc5t583_irq_set_wake()` form the IRQ chip. `rc5t583_irq()` is the threaded parent handler. `rc5t583_irq_init()` initializes registers, maps child IRQs, and requests the parent IRQ.

## Control Flow
Init rejects missing `irq_base`, clears cached enable/edge registers in hardware, disables master interrupt enables, clears pending interrupt registers, stores base/parent IRQ, assigns each Linux IRQ a chip and simple handler, marks them nested, and requests the parent threaded IRQ. On interrupt, the handler reads master status, reads only active group status registers, remaps RTC bits to logical order, clears status, merges GPIO falling/rising status, and calls `handle_nested_irq()` for enabled logical IRQs.

## State And Persistence
State is stored in the parent `struct rc5t583`: cached group enable masks, interrupt enable registers, GPIO edge registers, master enable register, base IRQ, parent IRQ, and mutex. Hardware mask and edge registers are synchronized on bus unlock.

## Dependencies And Integration Points
It depends on register helpers and constants from `linux/mfd/rc5t583.h`, the RC5T583 core probe, Linux nested IRQ APIs, and child devices that use contiguous IRQ numbers starting at platform-data `irq_base`.

## Risks
The unmask path updates `group_irq_en[data->grp_index]` but the dispatch path indexes `group_irq_en[data->master_bit]`, so this code relies on the chosen mapping and is fragile. Only GPIO IRQs support edge type changes; other type requests fail. The driver uses legacy fixed IRQ bases rather than irq_domain allocation. Status clear writes use inverted status bytes, requiring hardware-specific semantics.

## Test Signals
Validate every logical IRQ mapping, GPIO rising/falling/both-edge programming, RTC bit remapping, mask/unmask sync writes, wake propagation to parent IRQ, parent threaded IRQ dispatch, `irq_base` absence, and child devices receiving nested interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/rc5t583-irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/rc5t583.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/rc5t583.c

## Purpose
`rc5t583.c` is the I2C MFD core for the Ricoh RC5T583 PMIC. It initializes regmap caching, clears external power-request/deep-sleep configuration, optionally initializes custom IRQ support, exports external power request configuration, and registers GPIO, regulator, RTC, and key children.

## Important APIs, Types, And Functions
`deepsleep_data[]` maps deep-sleep resource IDs to sleep-sequence registers and bit positions. `rc5t583_ext_power_req_config()` is exported to child consumers. Private helpers configure PWRREQ1/PWRREQ2 and clear power request registers. `volatile_reg()` defines the regmap cache policy. `rc5t583_i2c_probe()` is the parent setup path.

## Control Flow
Probe requires platform data, allocates `struct rc5t583`, initializes an 8-bit cached regmap, clears ONOFFSEL/SWCTL and all sleep-sequence registers, initializes IRQs if an I2C IRQ exists, and adds MFD children. External power request configuration validates that PWRREQ1 and PWRREQ2 are not both selected, programs sleep-slot fields for most rails via PWRREQ1, handles DC0 through PWRREQ2, and enables ONOFFSEL bits.

## State And Persistence
Regmap cache covers many GPIO, interrupt, sleep-sequence, and regulator registers. Probe deliberately writes PMIC persistent runtime registers to clear previous external power request state. IRQ state is shared with `rc5t583-irq.c`.

## Dependencies And Integration Points
It depends on I2C, regmap with `REGCACHE_MAPLE`, legacy platform data including `irq_base` and shutdown enable, `linux/mfd/rc5t583.h`, the companion IRQ implementation, and child drivers `rc5t583-gpio`, `rc5t583-regulator`, `rc5t583-rtc`, and `rc5t583-key`.

## Risks
There is no DT match table and probe requires platform data, limiting modern firmware use. Clearing sleep-sequence registers at probe can override bootloader policy. IRQ initialization failures are only warnings, so children may probe without working IRQs. External request configuration writes several related registers and has special LDO4/DC0 cases.

## Test Signals
Test platform-data probe, regmap cache behavior for volatile/nonvolatile registers, external request setup and invalid combinations, clearing deep-sleep state, IRQ init success/failure, child registration, and PMIC register traces across reboot/shutdown-capable boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/rc5t583.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/rdc321x-southbridge.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/rdc321x-southbridge.c

## Purpose
`rdc321x-southbridge.c` is a small PCI MFD parent for RDC R-321x/R6030 southbridge functions. It enables the PCI device and exposes watchdog and GPIO logical children with I/O resource windows and shared southbridge platform data.

## Important APIs, Types, And Functions
`rdc321x_wdt_resource[]` and `rdc321x_gpio_resources[]` describe I/O register ranges. `rdc321x_wdt_pdata` and `rdc321x_gpio_pdata` carry the parent PCI device pointer, with GPIO also carrying `max_gpios`. `rdc321x_sb_cells[]` defines child devices `rdc321x-wdt` and `rdc321x-gpio`. `rdc321x_sb_probe()` performs setup.

## Control Flow
PCI probe calls `pci_enable_device()`, stores the parent `pci_dev` in both child platform-data structures, and calls `devm_mfd_add_devices()` to register the watchdog and GPIO children. The `module_pci_driver()` macro handles driver registration/removal.

## State And Persistence
State is static platform data plus devm-managed child devices. Hardware state is not modified beyond enabling the PCI device; watchdog/GPIO registers are left to child drivers.

## Dependencies And Integration Points
It depends on PCI vendor/device IDs `PCI_VENDOR_ID_RDC` and `PCI_DEVICE_ID_RDC_R6030`, MFD core, `linux/mfd/rdc321x.h`, and child drivers consuming I/O resources relative to the southbridge.

## Risks
The child platform-data structures are static globals, so multiple matching PCI devices would overwrite `sb_pdev`. There is no explicit `pci_disable_device()` callback in this file. Resource ranges are hard-coded and must match the child drivers' expectations.

## Test Signals
Probe on RDC hardware or emulation, child resource visibility, watchdog and GPIO child operation, repeated bind/unbind, and any multi-device scenario are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/rdc321x-southbridge.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/retu-mfd.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/retu-mfd.c

## Purpose
`retu-mfd.c` is the Nokia Retu/Tahvo I2C MFD core. It wraps a 16-bit SMBus register protocol in regmap, exposes synchronized read/write helpers, sets up variant-specific IRQ chips, registers child devices, and provides Retu poweroff through the watchdog.

## Important APIs, Types, And Functions
`struct retu_dev` stores regmap, device, mutex, and IRQ data. Exported APIs are `retu_read()` and `retu_write()`. `retu_bus` supplies custom regmap read/write callbacks over SMBus word operations. `retu_irq_chip` and `tahvo_irq_chip` describe power-button and VBUS interrupts. `retu_probe()`, `retu_remove()`, and `retu_power_off()` implement lifecycle.

## Control Flow
Probe chooses Retu or Tahvo data from I2C address, allocates state, initializes custom regmap, reads ASIC revision, masks all interrupts, adds a regmap IRQ chip, registers variant children with IRQ base from regmap-irq, and for Retu installs `pm_power_off` if free. Poweroff sets a control bit to ignore power-button state, writes watchdog zero, and loops forever waiting for shutdown.

## State And Persistence
The driver serializes all register access with a mutex. Hardware interrupt masks, watchdog, and power-control registers persist until changed or poweroff occurs. A global `retu_pm_power_off` tracks the Retu device owning `pm_power_off`.

## Dependencies And Integration Points
It depends on I2C SMBus word transfers, custom regmap bus support, regmap-irq, MFD core, `linux/mfd/retu.h`, OF/I2C IDs for `nokia,retu` and `nokia,tahvo`, and children `retu-wdt`, `retu-pwrbutton`, and `tahvo-usb`.

## Risks
Variant selection by I2C address (`addr - 1`) is unusual and assumes board layout. The custom regmap callbacks use `BUG_ON()` for size contract violations. Poweroff loops forever after watchdog write. Remove clears global `pm_power_off` unconditionally for the owner, so multi-poweroff interactions must be considered.

## Test Signals
Probe both Retu and Tahvo addresses, read ASIC revision, power-button and VBUS IRQ delivery, child IRQ bases, exported read/write serialization, poweroff behavior on Retu, remove cleanup, and SMBus error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/retu-mfd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/rk8xx-core.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/rk8xx-core.c

## Purpose
`rk8xx-core.c` is the shared MFD core for Rockchip RK801/RK805/RK806/RK808/RK809/RK816/RK817/RK818 PMICs. Bus-specific drivers supply a regmap and variant ID; the core selects IRQ chip, pre-initialization registers, child cells, poweroff/restart behavior, and suspend/resume pin policy.

## Important APIs, Types, And Functions
`struct rk808_reg_data` describes masked register writes. Variant arrays define child `mfd_cell`s, pre-init register scripts, and regmap IRQ tables. `rk808_power_off()`, `rk808_restart()`, `rk8xx_shutdown()`, `rk8xx_probe()`, `rk8xx_suspend()`, and `rk8xx_resume()` are the exported/shared entry points. Regmap IRQ chips exist for each variant family.

## Control Flow
`rk8xx_probe()` allocates `struct rk808`, selects variant-specific IRQ chip/pre-init/cells, optionally configures RK806 reset mode from `rockchip,reset-mode`, requires a core IRQ, registers a regmap IRQ chip, applies all pre-init masked writes, adds children with the IRQ domain, and if marked as a system power controller registers sys-off poweroff and sometimes restart handlers. Shutdown and PM callbacks adjust sleep/powerdown pin functions for supported variants.

## State And Persistence
Driver state includes variant ID, regmap, regmap IRQ chip data, and sys-off callbacks. Pre-init writes persist in PMIC runtime registers and include thermal thresholds, reset behavior, voltage monitor actions, codec defaults, interrupt polarity, and current limits.

## Dependencies And Integration Points
It depends on bus wrappers (`rk8xx-i2c.c`, `rk8xx-spi.c`), `linux/mfd/rk808.h`, regmap-irq, MFD core, sys-off/reboot APIs, device properties `system-power-controller`, `rockchip,system-power-controller`, and `rockchip,reset-mode`, plus regulator, RTC, pwrkey, pinctrl, clkout, codec, charger, and ADC child drivers.

## Risks
Pre-init scripts are large hardware policy tables; wrong values can affect rails, reset, thermal shutdown, audio, and charging. Core probe refuses missing IRQs, so boards without wired PMIC IRQ fail. RK817 codec registers include vendor-derived undocumented values. Poweroff/restart register choices are variant-specific and must remain aligned with PMIC IDs.

## Test Signals
Probe every variant through I2C/SPI as applicable, verify IRQ-domain child resources, pre-init register diffs, system poweroff/restart, shutdown pin-mode writes, suspend/resume pin behavior, RK806 reset-mode property, and child driver operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/rk8xx-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/rk8xx-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/rk8xx-i2c.c

## Purpose
`rk8xx-i2c.c` is the I2C bus wrapper for Rockchip RK8xx PMICs. It selects the correct regmap configuration and variant ID from OF match data, creates an I2C regmap, and delegates common setup to `rk8xx_probe()`.

## Important APIs, Types, And Functions
`struct rk8xx_i2c_platform_data` pairs a `regmap_config` with a variant constant. Variant-specific volatile-register callbacks define cache policy for RK801, RK806, RK808/RK805/RK818, RK816, and RK817/RK809. `rk8xx_i2c_probe()` initializes regmap and calls the core. `rk8xx_i2c_shutdown()` delegates to `rk8xx_shutdown()`, and PM ops delegate to `rk8xx_suspend()`/`rk8xx_resume()`.

## Control Flow
Probe reads match data, initializes the variant regmap with `devm_regmap_init_i2c()`, and passes `client->irq` and the variant ID to `rk8xx_probe()`. Shutdown and suspend/resume are thin pass-throughs to the shared core.

## State And Persistence
State is mostly regmap cache configuration. Volatile register policies determine which PMIC values are cached versus read live. Persistent hardware state is written by the shared core and child drivers, not by this wrapper beyond regmap access.

## Dependencies And Integration Points
It depends on I2C, OF compatibles `rockchip,rk801`, `rk805`, `rk806`, `rk808`, `rk809`, `rk816`, `rk817`, and `rk818`, regmap cache backends, and exported core functions from `rk8xx-core.c`.

## Risks
RK809 intentionally reuses the RK817 regmap config. RK817 uses `REGCACHE_NONE`, while other variants use cached regmaps; changing volatile lists can cause stale status or excessive I2C traffic. Passing a zero IRQ causes the core to fail, so firmware must provide the PMIC IRQ.

## Test Signals
Verify each compatible maps to the expected variant and max register, volatile registers bypass cache, IRQ propagation to the core, shutdown and PM callbacks, and error handling for regmap init failure or missing match data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/rk8xx-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/rk8xx-spi.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/rk8xx-spi.c

## Purpose
`rk8xx-spi.c` is the SPI bus wrapper for the Rockchip RK806 PMIC. It implements the RK806 SPI command framing as a custom regmap bus and delegates PMIC setup to the shared RK8xx core.

## Important APIs, Types, And Functions
`RK806_CMD_WITH_SIZE()` composes read/write command bytes with CRC disabled and transfer length. `rk806_spi_bus_write()` and `rk806_spi_bus_read()` implement custom regmap bus operations. `rk806_regmap_config_spi` defines a 16-bit register, 8-bit value regmap with volatile ranges. `rk8xx_spi_probe()` creates the regmap and calls `rk8xx_probe()` with `RK806_ID`.

## Control Flow
Regmap write receives address plus data, validates payload size, sends a command byte followed by the original register/value buffer in two SPI transfers. Regmap read validates two-byte address and value length, sends command plus address, and reads the requested value bytes. Probe initializes the custom regmap and hands it to the core with the SPI IRQ.

## State And Persistence
The wrapper stores no private state beyond the devm regmap. Hardware state is accessed through SPI commands and managed by the shared core and child drivers. Regmap cache uses `REGCACHE_MAPLE` with volatile ranges for power enable and DVS/IRQ registers.

## Dependencies And Integration Points
It depends on SPI, regmap custom buses, `linux/mfd/rk808.h`, OF compatible `rockchip,rk806`, SPI ID `rk806`, and `rk8xx_probe()` from the shared core.

## Risks
The RK806 SPI protocol uses two-byte little-endian register addresses and a command length field limited by `RK806_CMD_LEN_MSK`; regmap bulk accesses beyond that fail. CRC is explicitly disabled in commands. Unlike the I2C wrapper, this file does not install shutdown or PM callbacks, so RK806 SPI behavior depends on generic device handling and core sys-off registration.

## Test Signals
SPI read/write traces for single and bulk accesses, invalid transfer length handling, volatile range cache behavior, RK806 core probe via SPI IRQ, child regulator/pwrkey operation, and bind/unbind cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/rk8xx-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/rn5t618.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/rn5t618.c

## Purpose
`rn5t618.c` is the I2C MFD core for Ricoh RN5T567/RN5T618/RC5T619 PMICs. It initializes regmap, registers variant-specific children, optionally creates an RC5T619 regmap IRQ chip, and provides PMIC-driven poweroff/restart handling.

## Important APIs, Types, And Functions
`rn5t618_cells[]` and `rc5t619_cells[]` define child sets. `rn5t618_volatile_reg()` defines cache policy. `rc5t619_irq_chip` maps top-level RC5T619 interrupt groups. `rn5t618_irq_init()` registers IRQ support where available. `rn5t618_trigger_poweroff_sequence()`, `rn5t618_power_off()`, and `rn5t618_restart()` control shutdown and reboot. Probe/remove and PM callbacks handle lifecycle.

## Control Flow
Probe allocates `struct rn5t618`, selects variant from OF match data, creates an 8-bit cached regmap, adds RC5T619 or RN5T618 child devices, stores a global I2C client for poweroff, installs `pm_power_off` if the node is a system power controller, registers a high-priority restart handler, and initializes IRQ support. Remove clears global poweroff state for the owning client and unregisters restart. Suspend disables the physical IRQ; resume re-enables it.

## State And Persistence
Driver state includes variant, IRQ, regmap, IRQ data, global poweroff I2C client, and restart notifier. Poweroff/restart writes `RN5T618_REPCNT` and `RN5T618_SLPCNT`, which directly control PMIC shutdown/repower behavior.

## Dependencies And Integration Points
It depends on I2C, regmap, regmap-irq, MFD core, reboot notifier APIs, `linux/mfd/rn5t618.h`, compatibles `ricoh,rn5t567`, `ricoh,rn5t618`, and `ricoh,rc5t619`, and child drivers for regulators, watchdog, ADC, power, RTC, and related functions.

## Risks
IRQ support exists only for RC5T619; other variants with an IRQ return `-ENOENT`, which can fail probe after children and restart handler registration. The global restart handler is shared and not per-device safe for multiple PMICs. Remove clears `pm_power_off` whenever the owning client matches, without checking whether another driver installed a replacement. Suspend disables the IRQ without wake handling.

## Test Signals
Probe all variants, child set selection, RC5T619 IRQ delivery, non-RC5T619 IRQ behavior, poweroff and restart sequences, system-power-controller property, suspend/resume IRQ balance, and multi-device/global handler edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/rn5t618.c -->
