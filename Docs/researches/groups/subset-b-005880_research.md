# subset-b-005880 Research

Grouped research report for Linux MFD headers under `sources/distributed-fs/ceph-client/include/linux/mfd/`. Each section is delimited for reconciliation into the mapped per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/palmas.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/palmas.h

## Purpose
`palmas.h` is the central public interface for TI Palmas-family PMIC MFD children. It describes chip identity, register block addressing, regulator IDs, IRQ numbers, GPADC channels, USB/OTG state, resource-control data, platform data, and regmap access helpers used by the MFD core and child drivers. It covers both Palmas and TPS65917 variants and is intentionally broad because regulators, RTC, GPADC, USB/extcon, GPIO/pad mux, LED/PWM, resource, and charger-related children all share this single chip register map.

## Important APIs, Types, And Constants
The top-level `struct palmas` stores the device, up to `PALMAS_NUM_CLIENTS` I2C clients/regmaps, detected `id`, feature flags, IRQ state (`irq`, `irq_mask`, `irq_lock`, `irq_data`), PMIC driver data, child pointers, and mux bookkeeping. `is_palmas()`, `is_palmas_charger()`, `PALMAS_PMIC_FEATURE_SMPS10_BOOST`, and `PALMAS_PMIC_HAS()` gate variant-specific paths. `struct palmas_pmic_driver_data` describes regulator ranges, matches, sleep requestor mappings, and callback hooks for SMPS/LDO registration. `struct palmas_pmic_platform_data`, `struct palmas_reg_init`, `struct palmas_resource_platform_data`, `struct palmas_clk_platform_data`, `struct palmas_gpadc_platform_data`, and `struct palmas_platform_data` carry board/device-tree-derived policy into children. The exported inline helpers are `palmas_read()`, `palmas_write()`, `palmas_bulk_write()`, `palmas_bulk_read()`, `palmas_update_bits()`, and `palmas_irq_get_virq()`. `palmas_ext_control_req_config()` is the non-inline API for enabling or disabling external requestor control.

## Control Flow And State
There is no probe routine here, but the header defines the access flow. Callers pass a logical base such as `PALMAS_SMPS_BASE`, `PALMAS_RTC_BASE`, `PALMAS_RESOURCE_BASE`, `PALMAS_USB_BASE`, or `PALMAS_GPADC_BASE`; `PALMAS_BASE_TO_SLAVE()` selects the regmap client and `PALMAS_BASE_TO_REG()` derives the register offset before calling regmap. IRQ consumers use the enumerated Palmas or TPS65917 IRQ IDs with `palmas_irq_get_virq()`. Regulator/resource control flows through platform data and `palmas_ext_control_req_config()`, which maps requestor IDs such as SMPS, LDO, REGEN, SYSEN, and clock requestors to ENABLE1/ENABLE2/NSLEEP control bits.

## State And Persistence Behavior
Most state is hardware-backed: regulator voltage/mode registers, sleep/requestor assignments, RTC time/alarm and backup registers, GPADC calibration, USB detection state, interrupt masks/status, mux registers, and feature identity. Runtime-only state includes child driver pointers, mutexes, cached regulator range/current mode/ramp delay arrays, USB delayed work/debounce status, and muxed resource flags. Several register fields affect persistent power behavior across suspend, warm reset, and low-power states, especially `warm_reset`, `roof_floor`, sleep mode fields, and NSLEEP/ENABLE assignment registers. Incorrect writes can survive until reset or change board power sequencing.

## Dependencies And Integration Points
The header depends on regmap, regulator core, LED types, extcon, USB OTG, and USB phy companion declarations. It is consumed by MFD core code plus regulator, RTC, GPADC/IIO, USB/extcon, GPIO/pinctrl-like, resource, clock, LED, and power-management children. The multi-client regmap convention is an important integration point: every child must use the logical base constants rather than hard-coded I2C addresses. IRQ integration is via `regmap_irq_chip_data`.

## Risks
The main risk is register-map drift: this file contains thousands of offset, mask, and shift definitions, including variant-specific Palmas versus TPS65917 names. A wrong base, slave index, mask, or requestor ID can write the wrong physical register. External requestor control can disable rails unexpectedly if enable bits are mis-associated. The USB struct contains mixed IRQ and GPIO-detection paths, so link state can be wrong if debounce or enable flags are inconsistent. The macro `comparator_to_palmas()` refers to a `comparator` member that is not present in the visible `struct palmas_usb`, which is a compatibility/bitrot signal for users of that macro.

## Test Signals
Useful tests are compile coverage for all child drivers including Palmas and TPS65917 variants, regmap-irq mapping checks for expected virtual IRQs, regulator enable/voltage/suspend-mode tests, suspend/resume and warm-reset behavior on hardware, RTC alarm and backup-register tests, GPADC channel/current-source validation, and USB ID/VBUS extcon transitions through both IRQ and GPIO paths. Static checks should flag missing include dependencies and stale struct-member macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/palmas.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/pf1550.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/pf1550.h

## Purpose
`pf1550.h` declares the register map and shared MFD data for the NXP/Freescale PF1550 PMIC. It is a contract between the PF1550 core driver and child drivers for regulators, charger, onkey, interrupts, and OTP/DVS behavior.

## Important APIs, Types, And Constants
`enum pf1550_pmic_reg` lists device identity, interrupt status/mask/sense registers, regulator voltage/control registers, sequencing registers, charger registers, test/key registers, and the `PF1550_PMIC_REG_END` maximum. `enum pf1550_otp_reg` identifies OTP addresses used to read DVS enable bits. Constants describe device ID, OTP unlock keys, charger states, battery states, VBUS bits, charger field masks, ONKEY reset enable, DVS enable bits, top-level IRQ categories, sub-IRQ masks, and regulator IDs. IRQ domains are split across `enum pf1550_irq`, `enum pf1550_pmic_irq`, `enum pf1550_onkey_irq`, and `enum pf1550_charg_irq`. `struct pf1550_ddata` stores four regmap IRQ chip data pointers, the shared regmap, device pointer, DVS capability booleans, and the parent IRQ.

## Control Flow And State
The header has no functions, but it defines the expected core flow. Probe reads identity registers, unlocks OTP using PMIC/charger/test keys as needed, fills `dvs1_enable` and `dvs2_enable`, creates regmap IRQ chips for top-level, regulator, charger, and onkey interrupt groups, then exposes regulator and charger children. Interrupt handling is hierarchical: `PF1550_PMIC_REG_INT_CATEGORY` reports top-level categories, then child IRQ chips read group status/mask/sense registers such as SW, LDO, TEMP, ONKEY, MISC, or charger interrupt registers.

## State And Persistence Behavior
Register state includes regulator voltage, standby/sleep voltages, control mode, power-down sequencing, charger configuration, VBUS/battery/thermal status, ONKEY reset behavior, and interrupt masks. OTP state is persistent in hardware and controls whether DVS for SW1/SW2 is available. The data struct itself is runtime-only and caches the regmap/IRQ handles and DVS booleans.

## Dependencies And Integration Points
The header depends on I2C and regmap APIs. It integrates with Linux MFD, regmap-irq, regulator, charger/power-supply, and input/onkey drivers. Register naming separates PMIC and charger blocks but both are accessed through the same regmap address space.

## Risks
OTP key handling is sensitive because using the wrong unlock sequence can expose or modify protected areas. IRQ masks are split by category, and some bit values repeat in different groups; consumers must use the enum/mask for the correct status register. Charger-state constants are numeric hardware encodings, so off-by-one translations can report incorrect charging state. DVS enable flags must match OTP or the regulator driver may try unsupported voltage switching.

## Test Signals
Compile tests should cover regulator, charger, and onkey children. Hardware or regmap-sim tests should verify identity matching, OTP DVS detection, IRQ category fan-out, charger status decoding, VBUS/battery state reporting, and regulator sleep/standby voltage programming. Suspend and shutdown tests should inspect power-down sequence registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/pf1550.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/qcom_rpm.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/qcom_rpm.h

## Purpose
`qcom_rpm.h` is a small public interface for Qualcomm RPM MFD users. It hides the concrete RPM controller behind `struct qcom_rpm` and exposes the write operation used by RPM resource clients.

## Important APIs, Types, And Constants
The file forward-declares `struct qcom_rpm`, defines `QCOM_RPM_ACTIVE_STATE` and `QCOM_RPM_SLEEP_STATE`, and declares `qcom_rpm_write(struct qcom_rpm *rpm, int state, int resource, u32 *buf, size_t count)`. The buffer/count pair represents resource payload words for a target RPM state.

## Control Flow And State
Client drivers obtain or are passed an RPM handle by platform/MFD code, build a resource-specific `u32` payload, choose active or sleep state, and call `qcom_rpm_write()`. Control flow and transport details are implemented outside this header, likely serializing writes to RPM firmware and returning a negative errno on failure.

## State And Persistence Behavior
State lives in RPM firmware/hardware, not in this header. Writes can affect active-state behavior immediately or sleep-state behavior that persists until the next low-power transition or subsequent update. The header does not define caching, locking, or ownership rules.

## Dependencies And Integration Points
The only direct dependency is `linux/types.h`. Integration points are Qualcomm regulators, clocks, bus scaling, power domains, or other RPM resource consumers that share the opaque RPM controller.

## Risks
`state` and `resource` are plain integers, so call sites can accidentally pass invalid IDs without type safety. The payload is a mutable `u32 *` rather than `const u32 *`, so implementers and callers must agree whether the buffer may be modified. Count units are words, not bytes; confusing the two would corrupt messages.

## Test Signals
Build coverage should include every RPM client using this declaration. Unit or integration tests should validate active versus sleep writes, invalid resource handling, payload length checking, and error propagation from the RPM transport.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/qcom_rpm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/qnap-mcu.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/qnap-mcu.h

## Purpose
`qnap-mcu.h` defines the shared interface for a QNAP MCU MFD core and its child devices. It centralizes variant data and command execution helpers for features such as drive bays, fan control, and LEDs.

## Important APIs, Types, And Constants
The file forward-declares `struct qnap_mcu`. `struct qnap_mcu_variant` records serial baud rate, number of drives, minimum and maximum fan PWM values, and whether a USB LED exists. `qnap_mcu_exec()` sends command bytes and receives a reply. `qnap_mcu_exec_with_ack()` sends command bytes and expects an acknowledgment without exposing a caller-provided reply buffer.

## Control Flow And State
Child drivers compose MCU command frames and call the core execution function. The core likely serializes commands over UART/serdev, validates reply size, and returns status. Variant data selected by compatible string determines valid fan PWM ranges, drive count, and optional LED functionality. The ack helper is a convenience path for state-changing commands where a structured reply is not needed.

## State And Persistence Behavior
The header has no stateful implementation, but MCU state is external and can include fan PWM duty, LED state, drive presence/status, and controller firmware behavior. Runtime state is hidden inside `struct qnap_mcu`. Commands may change persistent or semi-persistent MCU settings depending on firmware.

## Dependencies And Integration Points
The header depends on `linux/types.h`. It integrates with MFD core, hwmon/fan, LED, storage-bay, or platform child drivers. Command buffer size and reply layout are firmware ABI, so all child drivers depend on the same framing semantics.

## Risks
Command/reply buffers are raw `u8` arrays with explicit sizes, so callers must avoid stack lifetime mistakes, undersized replies, and protocol mismatches. Fan PWM min/max are variant-specific and should be enforced before sending commands. A wrong variant can expose non-existent drives or LEDs.

## Test Signals
Tests should cover command serialization, reply length validation, ack success/failure paths, timeout/error propagation, variant selection, fan PWM clamping, and optional USB LED handling. Hardware-in-loop tests should confirm command ordering and concurrent child access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/qnap-mcu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/rave-sp.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/rave-sp.h

## Purpose
`rave-sp.h` exposes the shared command and event interface for the Zodiac RAVE Supervisory Processor MFD driver. It is used by child drivers that need firmware/version data, watchdog control, EEPROM access, reset reason, GPIO state, backlight control, or event notifications.

## Important APIs, Types, And Constants
`enum rave_sp_command` lists firmware, bootloader, board revision, GPIO, status, watchdog, EEPROM, backlight, reset, I2C-device status, silicon revision, and event-control commands. `struct rave_sp` is opaque. `rave_sp_action_pack()`, `rave_sp_action_unpack_event()`, and `rave_sp_action_unpack_value()` encode event/value pairs into a notifier action. `rave_sp_exec()` sends a command frame and receives a reply. `devm_rave_sp_register_event_notifier()` registers a managed notifier block for SP events.

## Control Flow And State
Child drivers build command payloads, call `rave_sp_exec()`, and decode replies. Event-capable users register a notifier; the MFD core receives events from the SP, packs event/value into an unsigned long action, and dispatches through the notifier chain. Device-managed registration ties notifier lifetime to the child device.

## State And Persistence Behavior
Hardware state includes watchdog configuration, reset cause, backlight level, EEPROM contents, event enablement, and firmware data. Runtime notification state is stored in the core and notifier registrations. The action packing is transient and only valid for notification dispatch.

## Dependencies And Integration Points
The header depends on Linux notifier APIs and forward-declares `struct device`. It integrates with watchdog, nvmem/EEPROM, backlight, reset, GPIO/status, and board-management child drivers. The command values are firmware ABI and must match SP firmware.

## Risks
The command ABI uses raw buffers and sizes, so command-specific length mistakes are likely failure points. Notifier action packing only preserves one byte of event and one byte of value; larger values would be truncated by design. Firmware version differences can make commands unavailable or semantically different.

## Test Signals
Tests should validate command framing and reply sizes, notifier registration/unregistration lifetime, event packing/unpacking round trips, watchdog pet/control commands, reset reason reads, and unavailable-command error handling across firmware revisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/rave-sp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/rc5t583.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/rc5t583.h

## Purpose
`rc5t583.h` is the shared interface for the Ricoh RC5T583 PMIC MFD. It describes register addresses for interrupts, regulators, GPIO, RTC, sleep sequencing, and provides inline regmap access helpers plus core IRQ/external-power APIs.

## Important APIs, Types, And Constants
The file defines limits for main/group interrupts and GPIO edge registers. It enumerates IRQs for system, DCDC, RTC, ADC, and GPIO sources; GPIO IDs; deep-sleep resource IDs; external power request controls; and regulator IDs. `struct rc5t583` stores the device, regmap, chip IRQ, IRQ base, IRQ lock, cached group enable bits, cached INTC enable byte, group enable registers, and GPIO edge registers. `struct rc5t583_platform_data` carries IRQ/GPIO bases, shutdown enable, regulator deep-sleep slots, external power-control masks, and regulator init data. Inline helpers wrap regmap write/read/update operations, and non-inline declarations expose `rc5t583_ext_power_req_config()`, `rc5t583_irq_init()`, and `rc5t583_irq_exit()`.

## Control Flow And State
The MFD core initializes the regmap and `struct rc5t583`, calls IRQ setup with the physical IRQ and optional base, and creates children. Children use inline helpers through their parent device drvdata. Regulator code uses platform data and `rc5t583_ext_power_req_config()` to bind a regulator or GPIO output to external PWRREQ1/PWRREQ2 sleep control and a deep-sleep slot. IRQ code maintains cached enable and edge registers under `irq_lock`, writes enable/mask/clear registers, and maps hardware events to Linux IRQs.

## State And Persistence Behavior
Hardware-backed state includes sleep sequence slots, regulator on/off/voltage/deep-sleep voltage registers, GPIO direction/output/edge/debounce/inversion state, RTC registers, ADC thresholds, and interrupt monitor/clear registers. Runtime cached state in `struct rc5t583` mirrors interrupt enables and GPIO edge configuration so IRQ operations can update hardware consistently.

## Dependencies And Integration Points
The header depends on mutex, types, and regmap, and references regulator init data. It integrates with MFD core, regmap, regulator, GPIO, RTC, ADC, and IRQ subsystems. Platform data is important for older board files.

## Risks
Inline helpers assume `dev_get_drvdata(dev)` is an initialized `struct rc5t583`; wrong parent device usage will dereference invalid data. Interrupt state is split across main and group registers with cached copies, so locking and cache synchronization are critical. External power request control can change regulator behavior during sleep and may break suspend/resume if slot IDs or masks are wrong.

## Test Signals
Build tests should cover child drivers using inline helpers. Hardware/regmap tests should verify IRQ init/exit, group enable caching, GPIO edge setup, regulator deep-sleep slot programming, external PWRREQ behavior, RTC alarm events, and read/write/update error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/rc5t583.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/rdc321x.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/rdc321x.h

## Purpose
`rdc321x.h` provides shared definitions for the RDC321x southbridge MFD children, specifically GPIO and watchdog blocks implemented as offsets in PCI configuration space.

## Important APIs, Types, And Constants
The header defines config-register offsets for watchdog control, GPIO control/data register pairs, and `RDC321X_NUM_GPIO` set to 59. `struct rdc321x_gpio_pdata` passes a southbridge `struct pci_dev *` and maximum GPIO count to the GPIO child. `struct rdc321x_wdt_pdata` passes the same PCI device to the watchdog child.

## Control Flow And State
The MFD core owns discovery of the southbridge PCI device and instantiates GPIO/watchdog children with platform data. Children use `sb_pdev` to read/write PCI config offsets such as `RDC321X_GPIO_CTRL_REG1`, `RDC321X_GPIO_DATA_REG1`, `RDC321X_GPIO_CTRL_REG2`, `RDC321X_GPIO_DATA_REG2`, and `RDC321X_WDT_CTRL`.

## State And Persistence Behavior
State is in PCI configuration registers, not in this header. GPIO direction/data and watchdog control affect hardware immediately and may persist until reset depending on chipset behavior. Platform data stores only pointers and bounds.

## Dependencies And Integration Points
The file depends on Linux types and PCI declarations. It integrates with the PCI core, MFD platform-device creation, GPIO subsystem, and watchdog subsystem.

## Risks
Accessing PCI config registers through a shared southbridge device requires careful serialization in child drivers. `max_gpios` must not exceed the hardware count. Wrong offsets can affect unrelated southbridge functions because this is not a normal MMIO register block.

## Test Signals
Tests should verify child devices receive a valid PCI device, GPIO count is clamped to 59, register offsets match chipset documentation, watchdog enable/disable works, and GPIO control/data operations do not corrupt adjacent PCI config fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/rdc321x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/retu.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/retu.h

## Purpose
`retu.h` is a compact interface for Nokia Retu/Tahvo MFD children. It exposes read/write helpers and shared register/interrupt constants for watchdog, common control, status, and Tahvo VBUS detection.

## Important APIs, Types, And Constants
The file forward-declares `struct retu_dev`, declares `retu_read(struct retu_dev *, u8)` and `retu_write(struct retu_dev *, u8, u16)`, and defines `RETU_REG_WATCHDOG`, `RETU_REG_CC1`, and `RETU_REG_STATUS`. It also defines `TAHVO_INT_VBUS` and `TAHVO_STAT_VBUS`.

## Control Flow And State
Child drivers call `retu_read()` and `retu_write()` on the shared device object to access registers. A Tahvo VBUS interrupt maps to bit 0 and status mask `TAHVO_STAT_VBUS`, allowing USB/charger children to detect VBUS state changes. Watchdog children use the watchdog register through the same accessors.

## State And Persistence Behavior
All meaningful state is hardware-backed in Retu/Tahvo registers. The watchdog register affects reset behavior, common control configures shared PMIC behavior, and status reflects current hardware state. The opaque `retu_dev` holds runtime transport/locking details outside the header.

## Dependencies And Integration Points
This header relies on `u8`/`u16` types from includers or common kernel headers. It integrates with MFD core, watchdog, USB/VBUS or charger detection, and platform-specific Nokia device support.

## Risks
The header does not include `linux/types.h`, so it relies on include-order context for `u8` and `u16`. Register accessors use raw register numbers and values, so child drivers must know field masks. Retu and Tahvo share related interfaces but not necessarily all registers, so consumers must avoid applying constants to the wrong chip.

## Test Signals
Compile tests should catch include-order regressions. Functional tests should cover read/write error propagation, watchdog programming, VBUS status/interrupt handling, and correct behavior on both Retu and Tahvo variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/retu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/rk808.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/rk808.h

## Purpose
`rk808.h` is the shared register and core-driver interface for the Rockchip RK8xx PMIC family. Despite the filename, it covers RK801, RK805, RK806, RK808, RK809, RK816, RK817, and RK818 variants, including regulators, RTC, interrupts, charger/fuel-gauge blocks, codec registers, sleep/reset controls, and core probe/suspend/resume/shutdown APIs.

## Important APIs, Types, And Constants
The header defines regulator ID enums for RK808, RK816, RK818, RK801, RK805, RK806, RK817, and RK809. It maps RTC, regulator enable/voltage/sleep registers, interrupt status/mask registers, battery/charger/fuel-gauge registers, codec registers for RK817, OTP/trim/test areas, DVS controls, and reset/sleep configuration fields. IRQ constants exist per variant, including RK816 grouped IRQs, RK806 two-byte interrupt status, RK808/RK818 IRQ masks, and RK817 extended charger/codec interrupts. `struct rk808` stores the device, regmap IRQ chip data, regmap, variant ID, regmap config, and regmap IRQ chip. Core APIs are `rk8xx_shutdown()`, `rk8xx_probe()`, `rk8xx_suspend()`, and `rk8xx_resume()`.

## Control Flow And State
Bus-specific drivers create a regmap, identify the PMIC variant, and call `rk8xx_probe(dev, variant, irq, regmap)`. The core uses the variant to choose register ranges, IRQ chip data, and child devices. Regulator children use the per-variant ID enums and voltage/enable registers. RTC code uses common RK808-style or RK817-style RTC register blocks. Power-supply/fuel-gauge code uses RK816/RK817/RK818 charger and ADC/coulomb-counter registers. Suspend/resume flows use `rk8xx_suspend()` and `rk8xx_resume()` to handle IRQ wake, register configuration, or variant-specific low-power behavior. Shutdown calls `rk8xx_shutdown()` to program device-off/reset fields.

## State And Persistence Behavior
Hardware state spans RTC time/alarm, regulator voltages and sleep voltages, power-enable and sleep-enable bits, undervoltage thresholds/actions, hot-die thresholds, IRQ masks/status, charger configuration/status, fuel-gauge counters/calibration, OTP/trim fields, data registers, codec settings, sleep pin behavior, reset behavior, and DVS control. `struct rk808` is runtime-only but its `variant`, regmap config, and IRQ chip selection determine all child behavior. Some data registers and fuel-gauge counters preserve information across sleep or reset depending on silicon.

## Dependencies And Integration Points
The header depends on regulator machine data and regmap. It integrates with I2C/SPI bus glue, MFD core, regmap-irq, regulator, RTC, clk, power-supply/fuel-gauge, audio codec, input/power-key, and system poweroff/restart paths. It also defines SPI command bits for RK806, making bus framing part of the shared ABI.

## Risks
The file is highly variant-dense: many register numbers overlap with different meanings across chips, and duplicate names such as RK818 boost LDO voltage registers are intentionally repeated. Using an enum or mask with the wrong variant can write unrelated hardware. RK806 includes SPI command/CRC/length definitions and extensive OTP/trim registers, so transport and protected-register handling need extra care. Several APIs accept plain integer variant IDs; mismatches may compile but fail at runtime.

## Test Signals
Compile all enabled RK8xx children and both I2C/SPI bus paths. Runtime tests should verify variant detection, regmap range access, IRQ mapping and wake behavior, regulator voltage/enable/sleep settings for each variant, RTC alarms, power-key/hot-die events, charger/fuel-gauge measurements, RK817 codec register access, suspend/resume, shutdown/reset, and RK806 SPI framing including CRC/length handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/rk808.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/rn5t618.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/rn5t618.h

## Purpose
`rn5t618.h` defines the shared register map and MFD state for Ricoh RN5T618-family PMICs, including RN5T567 and RC5T619 variants. It supports regulators, RTC, ADC, GPIO, charger, fuel-gauge, watchdog, interrupt, and power-control children.

## Important APIs, Types, And Constants
The header lists register addresses from identity and power-control registers through regulator slots/controls, ADC data and thresholds, GPIO control, interrupt control, RTC, charger, and fuel-gauge/coulomb-counter areas. It defines important bit masks for watchdog, repower-on, software poweroff, power-off history, and watchdog IRQ. Regulator IDs enumerate DCDC1-5, LDO1-10, and LDORTC1/2. Variant IDs are `RN5T567`, `RN5T618`, and `RC5T619`. IRQ groups are `RN5T618_IRQ_SYS`, `DCDC`, `RTC`, `ADC`, `GPIO`, and `CHG`. `struct rn5t618` stores regmap, device, variant, IRQ number, and regmap IRQ chip data.

## Control Flow And State
The MFD core initializes the regmap, selects the variant, registers a regmap IRQ chip for grouped interrupt handling, and exposes children. Regulator children use the DCDC/LDO control and sleep-voltage registers. RTC code uses the RTC block. ADC and charger/power-supply drivers use ADC data/threshold and charger status/control registers. Watchdog or poweroff code uses watchdog, sleep, repower, and power function bits.

## State And Persistence Behavior
Hardware state includes regulator enable/voltage/sleep settings, power-on/off history, watchdog configuration, ADC thresholds and readings, GPIO direction/output/edge state, RTC time/alarm, charger state, battery/fuel-gauge capacity and coulomb-counter registers. `struct rn5t618` is runtime-only and ties child access to the chosen variant and IRQ chip.

## Dependencies And Integration Points
The header depends on regmap. It integrates with MFD core, regmap-irq, regulator, RTC, GPIO, ADC/IIO, charger/power-supply, watchdog, and system power-management code. Variant selection is central because child availability and register semantics can differ across RN5T567/RN5T618/RC5T619.

## Risks
The register space mixes regulator, ADC, GPIO, RTC, charger, and fuel-gauge blocks with plain macros; a wrong variant or offset can silently access the wrong function. Power-off history bits are latched hardware state and must be cleared/read carefully. Watchdog and software poweroff bits can reset or shut down the system if mishandled.

## Test Signals
Tests should validate variant-specific child creation, IRQ group mapping, regulator control, RTC alarms, ADC threshold events, GPIO edge interrupts, charger/fuel-gauge reporting, watchdog enable/timeout, power-off history decoding, and suspend/resume power behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/rn5t618.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/rohm-bd71815.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/rohm-bd71815.h

## Purpose
`rohm-bd71815.h` declares the shared register map, regulator IDs, interrupt IDs, and masks for the ROHM BD71815 PMIC. It supports regulator, RTC, charger, battery monitor/fuel gauge, LED/WLED, GPIO/GPO, clock, and interrupt child drivers.

## Important APIs, Types, And Constants
The first enum assigns regulator IDs for five bucks, LDO1-5, LDODVREF, LDOLPSR, WLED, and total count. The register enum maps device/power control, buck/LDO modes and voltages, LED, GPO, 32 kHz output, RTC time/alarms, charger state/configuration, battery and DCIN/VSYS status, ADC/measurement registers, coulomb counter registers, interrupt enable/status/update registers, REX/full counters, and test mode. Bit masks define buck ramp and power-state enables, DVS select/defaults, LDO modes, output clock mode, battery/DCIN status, RTC alarm, power-control restart, GPIO drive type, interrupt enable masks, individual interrupt IDs, interrupt bit masks, coulomb counter control, current direction, REX clear/state, and charge-done LED enable.

## Control Flow And State
The MFD core uses the register map and IRQ masks to configure regmap and regmap-irq. Regulator children use regulator IDs plus buck/LDO mode and voltage registers. RTC children use `BD71815_REG_RTC_START` and alarm start/mask definitions. Charger and battery drivers read charger state, battery status, voltage/current monitor registers, coulomb counter registers, and interrupt sources. LED/GPO/clock children use LED control, GPO, and OUT32K definitions.

## State And Persistence Behavior
Hardware-backed state includes rail modes, voltages, power-state participation, LED current/enables, GPIO output/drive, RTC time/alarms, charger state/configuration, watchdog, battery presence/temperature, voltage/current measurements, coulomb counts, and retained REX/full charge counters. Interrupt enable/status registers are persistent until changed or cleared according to hardware semantics. There is no runtime struct in this header.

## Dependencies And Integration Points
The header depends on regmap and integrates with ROHM MFD core code, regulator, RTC, power-supply/charger/fuel-gauge, LED, GPIO/GPO, clk, and regmap-irq subsystems. Interrupt definitions are organized by hardware status register groups and must match the regmap IRQ table.

## Risks
The register enum has non-contiguous blocks and explicit offsets, so inserting values incorrectly would shift later addresses. Interrupt names and masks are group-specific; reusing a mask against the wrong `INT_STAT_xx` register is a likely bug. Charger/battery monitor fields include signed direction bits, so current interpretation must preserve discharging flags. Some comments reference BD71805 while the file is BD71815, a documentation consistency risk.

## Test Signals
Tests should cover regulator mode/voltage programming, RTC read/alarm, charger state transitions, battery detection and temperature interrupts, coulomb counter enable/reset/current direction, LED and OUT32K control, GPIO drive/output, and regmap-irq mapping for all grouped masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/rohm-bd71815.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/rohm-bd71828.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/rohm-bd71828.h

## Purpose
`rohm-bd71828.h` provides the shared register and interrupt definitions for the ROHM BD71828 PMIC. It is used by child drivers for regulators, GPIO, 32 kHz clock, RTC, charger, battery/fuel gauge, LEDs, and interrupt handling.

## Important APIs, Types, And Constants
The regulator enum covers BUCK1-7, LDO1-6, LDO_SNVS, and total count. Voltage-count constants and masks describe selector ranges, including fixed 1.8 V LDO6. Register macros define mode control, run-level/DVS controls, buck/LDO enable/mode/voltage registers, GPIO control and IO status, OUT32K, RTC time and three alarm blocks, charger/battery status and ADC values, coulomb-counter/current/voltage measurement registers, LED control, interrupt mask/status/update registers, and maximum register. Main IRQ bit IDs aggregate BUCK, DCIN, VSYS, CHG, BAT, BAT_MON, TEMP, and RTC groups. The interrupt enum and per-interrupt masks define detailed events such as buck OCP, DCIN insertion/removal, button pushes, watchdog/reset, VSYS transitions, charger state, battery/thermal events, coulomb counter thresholds, overcurrent, temperature, and RTC alarms.

## Control Flow And State
The MFD core configures regmap/regmap-irq using the register and mask definitions. Regulator children use enable/mode/voltage registers and DVS/run-level masks. GPIO and clock children manipulate GPIO control and OUT32K registers. RTC uses contiguous time and alarm registers. Charger and fuel-gauge children read DCIN, battery, voltage/current, coulomb counter, and measurement-clear registers. Interrupt handling fans out from `BD71828_REG_INT_MAIN` to the group status registers.

## State And Persistence Behavior
Hardware-backed state includes regulator enable and low-power modes, DVS source, run levels, GPIO drive/output, RTC time/alarms, charger enable/state, DCIN/battery presence, voltage/current/coulomb measurements, LED state, and interrupt masks/status. Coulomb counter clear bits and measurement clear registers are stateful operations with side effects. This header has no runtime struct; state ownership lives in MFD core and child drivers.

## Dependencies And Integration Points
The header depends on `linux/bits.h`, `linux/mfd/rohm-generic.h`, and `linux/mfd/rohm-shared.h`. It integrates with ROHM common MFD support, regulator, RTC, GPIO, clk, LED, power-supply/fuel-gauge, and regmap-irq subsystems. The main/group IRQ split is a key integration contract.

## Risks
The register map is broad and includes repeated macro definitions such as `BD71828_REG_CHG_STATE`, so maintainers must avoid accidental redefinition drift. Interrupt masks are raw hex values grouped by register; using them outside the correct group will mis-handle events. Coulomb counter and battery-current direction masks require careful signed conversion. DVS/run-level control can alter CPU/SoC rail behavior if programmed incorrectly.

## Test Signals
Tests should verify regulator selector ranges and fixed LDO6 handling, DVS/run-level mode changes, GPIO output and drive modes, RTC alarms, charger enable and DCIN detection, battery presence/temperature, coulomb counter clear/read paths, LED masks, and regmap-irq main-to-group fan-out.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/rohm-bd71828.h -->
