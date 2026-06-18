# subset-b-005876 Research

Grouped research for Linux MFD headers under `sources/distributed-fs/ceph-client/include/linux/mfd`. Each section is bounded for reconciliation into a source-tree-aligned per-file report.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/da9063/registers.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/da9063/registers.h

Purpose: This header is the complete DA9063 PMIC register and bitfield map for Dialog Semiconductor DA9063 variants. It defines page selection behavior, system status/event/IRQ mask registers, GPIO controls, regulator controls, GPADC registers, RTC/calendar registers, sequencer registers, OTP/configuration registers, monitor registers, and chip identification registers. It is a shared ABI between the DA9063 MFD core and DA9063 child drivers.

Important APIs, types, and constants: The file exports macros only. Core address macros include `DA9063_REG_PAGE_CON`, `DA9063_REG_STATUS_A` through `DA9063_REG_STATUS_D`, `DA9063_REG_EVENT_A` through `DA9063_REG_EVENT_D`, `DA9063_REG_IRQ_MASK_A` through `DA9063_REG_IRQ_MASK_D`, regulator controls such as `DA9063_REG_BCORE*_CONT`, `DA9063_REG_LDO*_CONT`, GPADC controls, DA9063_AD and DA9063_BB alarm aliases, and variant ID masks. Bit macros cover event bits, mask bits, GPIO pin mux/type/no-wakeup controls, buck and LDO enable/configuration/voltage fields, ADC mux and result layout, RTC alarm/tick fields, monitor enable bits, and configuration bits such as buck merge and LDO8 vibrator mode.

Control flow, state, and persistence: There are no functions, so runtime control flow is in consumers. State lives in hardware registers, including latched fault/event registers, IRQ masks, RTC counters and alarms, regulator configuration and voltage selector registers, GPIO pin modes, OTP/config pages, and variant IDs. Page selection is critical because I2C/SPI addressing crosses several pages and DA9063_AD versus DA9063_BB aliases map the same logical features to different addresses.

Dependencies and integration points: Consumers normally combine this map with regmap, regmap-irq, regulator, RTC, GPIO/pinctrl, watchdog, ADC, and MFD child setup code. `linux/bitops.h` is not included here, so macros use raw hex masks rather than `BIT()`. Integration depends on matching register aliases to the probed silicon variant and matching event bits to the IRQ chip layout.

Risks and test signals: Risk is concentrated in off-by-one page addresses, using AD addresses on BB silicon or the reverse, stale mask definitions for merged bucks or LDO voltage biases, and clearing write-one-to-clear event bits accidentally. Test signals include probe/regmap readable-range tests, IRQ event/mask tests for all four event registers, regulator voltage selector round trips, RTC alarm/tick tests, GPIO mux tests, ADC mux/result decoding, and suspend/resume tests that verify persistent RTC and regulator state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/da9063/registers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/da9150/core.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/da9150/core.h

Purpose: This is the DA9150 MFD core interface. It defines paging constants, logical IRQ numbers, platform data, the parent `struct da9150`, and exported register and query-interface accessors used by DA9150 charger, fuel gauge, GPADC, and other child drivers.

Important APIs, types, and functions: `DA9150_REG_PAGE_SHIFT` and `DA9150_REG_PAGE_MASK` encode 16-bit register page addressing. `DA9150_NUM_IRQ_REGS` and IRQ numbers from `DA9150_IRQ_VBUS` through `DA9150_IRQ_WKUP` define the regmap IRQ namespace. `struct da9150_fg_pdata` carries fuel-gauge update and warning thresholds; `struct da9150_pdata` carries IRQ base and fuel-gauge platform data; `struct da9150` holds `dev`, `regmap`, the fuel-gauge query-interface I2C client, IRQ chip data, and IRQ bases. Exported helpers include `da9150_read_qif`, `da9150_write_qif`, `da9150_reg_read`, `da9150_reg_write`, `da9150_set_bits`, `da9150_bulk_read`, and `da9150_bulk_write`.

Control flow, state, and persistence: The core probes the I2C PMIC, initializes regmap and regmap-irq, and child drivers call these helpers rather than open-coding page selection. The query interface is a separate I2C endpoint used for fuel-gauge operations. Persistent state is in PMIC registers and firmware/fuel-gauge memory, while the in-kernel `struct da9150` tracks only live handles and IRQ metadata.

Dependencies and integration points: The header depends on device, I2C, interrupt, and regmap infrastructure. It integrates with `da9150/registers.h` for register addresses and bitfields, with MFD cell registration for children, and with the Linux IRQ and power-supply/charger stacks through child drivers.

Risks and test signals: Risks include incorrect page calculations, confusing standard register access with the query interface, and mismatched IRQ numbering relative to the regmap IRQ chip. Test signals include child-driver probe against a mocked regmap, IRQ mapping coverage for all 21 logical IRQs, bulk read/write boundary tests across page changes, and fuel-gauge query-interface transaction tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/da9150/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/da9150/registers.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/da9150/registers.h

Purpose: This header is the DA9150 PMIC register and bitfield catalog. It covers base page control, status, faults, events, IRQ masks, GPIO, GPADC, charger detection, VBUS/charger control, core firmware/bootloader registers, fuel-gauge/firmware download registers, coulomb counter, timers, auxiliary data, BIF, and battery temperature measurement.

Important APIs, types, and constants: The file exports macros only and includes `linux/bitops.h` for `BIT()`. Register addresses include `DA9150_STATUS_*`, `DA9150_EVENT_*`, `DA9150_IRQ_MASK_*`, configuration/control registers, adapter-detection registers, PPR charger registers, `DA9150_CORE*`, firmware-download fields, `DA9150_GPADC_*`, `DA9150_CC_*`, `DA9150_TAUX_*`, and `DA9150_TBAT_*`. Bitfields are consistently represented as `*_SHIFT` plus `*_MASK`, with named enum-like values for charger state, VBUS state, detected USB/ACA charger type, page write mode, and fault/event flags.

Control flow, state, and persistence: There are no executable paths. Runtime flow is indirect: the DA9150 core and child drivers select pages and then read/update registers through regmap helpers from `core.h`. Hardware state includes latched event and fault logs, charger algorithm status, VBUS/USB detection state, GPIO modes, GPADC conversion state, firmware download state, coulomb-counter accumulators, and battery temperature ADC data. Some fields represent long-lived configuration or firmware-controlled state.

Dependencies and integration points: The file integrates tightly with the DA9150 MFD core, regmap-irq, charger/power-supply drivers, fuel gauge, GPADC/IIO, GPIO, and firmware download logic. Consumers must combine masks with the correct page address and must honor hardware state-machine constraints for charger and firmware registers.

Risks and test signals: Risks include duplicate generic macro names such as `DA9150_PAGE_SHIFT` redefined for multiple page registers, using an unshifted value with a shifted mask, stale USB charger type values, and incorrect write timing for charger/core firmware state. Test signals include register-field unit tests where available, regmap trace review during charger attach/detach, GPADC conversion readback, IRQ mask/event acknowledgment tests, and firmware download error-path tests using `DA9150_FW_FWDL_ERR_MASK`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/da9150/registers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/davinci_voicecodec.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/davinci_voicecodec.h

Purpose: This header defines the TI DaVinci voice codec MFD core interface. It describes memory-mapped voice codec registers, interrupt and FIFO control bits, child cells, and shared parent state used by VCIF and CQ93VC child devices.

Important APIs, types, and constants: Register macros cover PID, control, interrupt enable/status/clear, emulation control, read/write FIFOs, FIFO status, test control, and codec-specific registers. Bit macros describe ADC/DAC reset, 8-bit/unsigned sample format, FIFO enable/clear/mode, interrupt masks, PGA gain, mute/digital attenuation, and power-all-on/off values. `enum davinci_vc_cells` names the VCIF and CQ93VC cells. `struct davinci_vcif` stores DMA channels and FIFO DMA addresses. `struct davinci_vc` stores the parent device, platform device, clock, MMIO base, regmap, MFD cells, and child VCIF data.

Control flow, state, and persistence: The parent driver maps hardware, enables the codec clock, initializes regmap, and registers two MFD child devices. Child audio drivers manipulate FIFO, interrupt, sample-format, and power fields. Runtime state is primarily in hardware FIFOs, interrupt status, and codec control registers; the C structs hold live resources and DMA routing.

Dependencies and integration points: The header depends on MFD core, clock, regmap, platform device, and DMA address types. It integrates with ALSA SoC codec/interface drivers and platform DMA channels.

Risks and test signals: Risks include FIFO overrun/underrun mask confusion, mismatched DMA addresses, clock enable ordering, and bit typo risk around `DAVINCI_VC_INT_WERROVF_MASKBIT`. Test signals include loopback audio capture/playback, interrupt storm/clear behavior, FIFO status under stress, runtime PM clock tests, and child cell probe ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/davinci_voicecodec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/db8500-prcmu.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/db8500-prcmu.h

Purpose: This file defines DB8500 PRCMU firmware constants and public firmware API prototypes for ST-Ericsson Ux500 power, reset, clock, wakeup, regulator, ABB, modem, and mailbox coordination. It is the DB8500-specific backend included by the generic `dbx500-prcmu.h` wrapper.

Important APIs, types, and functions: It defines registers such as DSI reset and line value bits, plus many firmware enums: power states, retention states, ARM/GEN clock schemes, romcode read/write values, AP power-state transitions, deprecated hardware-accelerator state, AP transition status/error codes, DVFS status, mailbox IDs, clock names, regulator IDs, and modem states. The exported `db8500_prcmu_*` functions include early init, power-state transitions, EPOD state changes, wakeup enable/configuration, ABB event readout, ABB read/write/masked write, direct register read/write/update, DDR/APE/ARM OPP controls, clock rate/enable/disable, reset control, modem reset, watchdog/thermal helpers, and IRQ registration paths.

Control flow, state, and persistence: Runtime flow goes through firmware mailboxes shared by the ARM side and the XP70 PRCMU firmware. Calls encode target states, wait for mailbox completions or status codes, and sometimes coordinate AP deep sleep and reset handshakes. Persistent or externally visible state is in PRCMU firmware memory, power-domain state, clocks, wakeup masks, ABB events, and hardware register blocks. Several operations cross suspend/resume and reset boundaries.

Dependencies and integration points: The header depends on interrupt and bitops APIs and is consumed by Ux500 platform power management, clock, regulator, reset, thermal, watchdog, modem, and IRQ code. It is wrapped by `dbx500-prcmu.h` for SoC selection.

Risks and test signals: Risks include firmware ABI drift, obsolete enum aliases, blocking in wrong context while waiting for firmware responses, incomplete error handling for mailbox status values, and using deprecated hardware accelerator paths instead of regulator APIs. Test signals include suspend/resume cycles, DVFS/OPP transition traces, wakeup-source tests, ABB read/write error injection, PRCMU IRQ delivery, watchdog reset tests, and clock rate verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/db8500-prcmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/dbx500-prcmu.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/dbx500-prcmu.h

Purpose: This header is the generic Ux500 PRCMU public API wrapper. It defines common PRCMU constants, firmware version metadata, wakeup and EPOD identifiers, OPP and DDR power-state enums, and inline wrappers that dispatch to DB8500 implementations when `CONFIG_UX500_SOC_DB8500` is enabled.

Important APIs, types, and functions: Important definitions include `PRCMU_WAKEUP()` and `enum prcmu_wakeup_index`, EPOD IDs and EPOD states, CLKOUT source IDs, watchdog IDs, APE/ARM/DDR OPP enums, firmware project IDs, and `struct prcmu_fw_version`. Inline wrappers include `prcmu_early_init`, `prcmu_set_power_state`, `prcmu_get_power_state_result`, `prcmu_set_epod`, `prcmu_enable_wakeups`, `prcmu_disable_wakeups`, ABB event helpers, and many additional wrappers/prototypes later in the file for clocks, resets, regulator-like domains, watchdog, modem, thermal, and IRQ registration. If DB8500 support is disabled, the API provides stubs or `-ENOSYS` style behavior where applicable.

Control flow, state, and persistence: This header has wrapper control flow only. The real state machine is the PRCMU firmware backend, but callers see stable generic names. Wakeup masks, EPOD state, OPP state, DDR power state, firmware version data, and watchdog state are persistent hardware/firmware state, not stored in this header.

Dependencies and integration points: It includes interrupt, notifier, err, device-tree clock IDs, and the DB8500-specific header. It integrates platform code with clock, reset, power-domain, regulator, suspend, and thermal subsystems while hiding DB8500 backend names.

Risks and test signals: Risks include building callers against generic APIs when the backend is disabled, stale project IDs, conflicts with unprefixed EPOD IDs, and diverging DB8500 wrapper signatures. Test signals include compile coverage with and without DB8500 config, suspend/resume and wakeup tests, EPOD/clock/reset smoke tests, and firmware version parsing for DB8500 versus DBX540 offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/dbx500-prcmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/dln2.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/dln2.h

Purpose: This header defines the shared interface for Diolan DLN-2 USB MFD subdrivers. It gives subdrivers a command encoding macro, per-subdevice platform data, event callback registration, and synchronous command transfer helpers.

Important APIs, types, and functions: `DLN2_CMD(cmd, id)` combines a command opcode with a module ID. `struct dln2_platform_data` carries the internal subdriver handle and port number. `dln2_event_cb_t` is an interrupt-context callback receiving the platform device, echo, payload pointer, and payload length. Exported functions are `dln2_register_event_cb`, `dln2_unregister_event_cb`, and `dln2_transfer`. Inline helpers `dln2_transfer_rx` and `dln2_transfer_tx` specialize transfers with only receive or transmit payloads.

Control flow, state, and persistence: Subdrivers register callbacks for DLN-2 events, issue command transfers through the parent USB transport, and receive event payloads in interrupt context. State is held by the parent driver, command handles, pending transfers, callback registrations, and per-port platform data; the payload pointer is explicitly valid only for the callback duration.

Dependencies and integration points: It integrates with platform-device MFD children for I2C, SPI, GPIO, and other DLN-2 functions. The implementation depends on the DLN-2 USB transport and parent event demultiplexer.

Risks and test signals: Risks include sleeping or doing heavy work in event callbacks, using the event data after return, not initializing `ibuf_len` before `dln2_transfer`, and command ID collisions. Test signals include USB disconnect during transfer, callback registration/unregistration races, oversized payload handling, per-port command routing, and interrupt-context lockdep coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/dln2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/ezx-pcap.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/ezx-pcap.h

Purpose: This file defines the Motorola EZX PCAP2 PMIC/MFD interface. It maps PCAP subdevices, register operations, IRQ translation, ADC access, regulator IDs, interrupt IDs, battery/ADC/USB/LED/RTC fields, and SPI command framing.

Important APIs, types, and functions: `struct pcap_subdev` and `struct pcap_platform_data` describe board-provided child devices, IRQ base, config flags, GPIO, and init callback. `struct pcap_chip` is opaque to children. Exported operations are `ezx_pcap_write`, `ezx_pcap_read`, `ezx_pcap_set_bits`, `pcap_to_irq`, `irq_to_pcap`, `pcap_adc_async`, and `pcap_set_ts_bits`. Register macros cover ISR/MSR, regulators, battery, ADC, audio codec, bus control, RTC, power, peripherals, and masks. Constants define 23 PCAP IRQs, regulator IDs, ADC banks/channels/timing modes, LED/backlight fields, and RTC masks.

Control flow, state, and persistence: The parent PCAP driver frames register read/write operations over the PCAP port, registers MFD children, maps PCAP IRQs into Linux IRQs, and services asynchronous ADC completion callbacks. Persistent state resides in PMIC registers for interrupts, regulators, RTC, ADC monitor configuration, battery charging, LEDs, and bus control.

Dependencies and integration points: It integrates with SPI/GPIO board setup, IRQ domain or legacy IRQ base mapping, regulator, RTC, input/touchscreen, battery, LED/backlight, audio, and USB/transceiver children.

Risks and test signals: Risks include 25-bit register value truncation, wrong port-specific register use, ADC callback lifetime issues, IRQ base translation errors, and regulator ID drift. Test signals include read/write framing tests, interrupt clear/mask tests, async ADC completion and timeout tests, RTC day/time boundary tests, LED/backlight field tests, and suspend/resume retention of regulator and RTC state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/ezx-pcap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/gsc.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/gsc.h

Purpose: This header defines the Gateworks System Controller MFD register interface and parent state. It maps the GSC I2C subaddresses, core registers, control and IRQ bit positions, and common regmap read/write callbacks.

Important APIs, types, and functions: Device-address macros identify miscellaneous control, update, GPIO, HWMON, EEPROM banks, and RTC I2C targets. The register enum defines control, time, IRQ status/enable, firmware CRC/version, and write-protect offsets. Bit constants define pushbutton actions, sleep/watchdog/switch-boot controls, and IRQ sources. `gsc_read` and `gsc_write` are regmap bus callbacks. `struct gsc_dev` stores the parent device, primary and HWMON I2C clients, regmap, firmware version, and CRC.

Control flow, state, and persistence: The parent driver instantiates multiple logical functions behind the controller's I2C addresses, provides regmap access to the misc block, and exposes child functionality for RTC, HWMON, GPIO, watchdog, or update paths. State persists in controller firmware registers, EEPROM, RTC, IRQ latches, and watchdog/sleep configuration.

Dependencies and integration points: It depends on regmap and I2C client users. It integrates with MFD children for hardware monitoring, RTC, GPIO, EEPROM/NVMEM, watchdog, and firmware update support.

Risks and test signals: Risks include bit-position macros being used as masks without `BIT()`, incorrect I2C subaddress routing, write-protect mistakes, and watchdog/sleep settings surviving reboot unexpectedly. Test signals include regmap read/write callback tests, IRQ source/mask tests, firmware version/CRC readback, HWMON child probe, RTC operation, and watchdog timeout behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/gsc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/hi6421-pmic.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/hi6421-pmic.h

Purpose: This small header defines the HiSilicon HI6421 PMIC core interface. It provides bus-address conversion, over-current protection debounce settings, the parent PMIC state, and chip type identifiers.

Important APIs, types, and constants: `HI6421_REG_TO_BUS_ADDR(x)` shifts logical register numbers for the PMIC bus format. `HI6421_REG_MAX` bounds register access. OCP debounce/control macros define register address, selection mask, debounce intervals from 8 ms to 64 ms, debounce enable, and auto-stop enable. `struct hi6421_pmic` holds the device, regmap, IRQ, and optional chip pointer. `enum hi6421_type` distinguishes supported PMIC variants.

Control flow, state, and persistence: Runtime flow is in the MFD core and child drivers that use regmap with shifted addresses. Hardware state includes OCP debounce policy, OCP auto-stop behavior, IRQ state, and regulator/PMIC registers behind this map. The header has no executable logic.

Dependencies and integration points: It integrates with regmap, IRQ handling, regulator children, and platform/DT matching for variant selection.

Risks and test signals: Risks include forgetting the two-bit bus-address stride, programming the wrong OCP debounce value, and incomplete variant matching. Test signals include regmap address translation checks, OCP interrupt/debounce testing, regulator child probe, and IRQ handling under fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/hi6421-pmic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/hi655x-pmic.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/hi655x-pmic.h

Purpose: This header defines common HiSilicon HI655x PMIC addressing, interrupt registers, version bounds, interrupt bit positions, and parent device state.

Important APIs, types, and constants: `HI655X_STRIDE` and `HI655X_BUS_ADDR(x)` encode the 4-byte bus address stride. IRQ constants define 32 interrupts over four status/mask bytes, base addresses for IRQ status/mask and analog IRQ masks, clear and mask values, version register and version range, individual interrupt bit positions, and corresponding `BIT()` masks. `struct hi655x_pmic` holds the device, regmap, IRQ, IRQ domain, and cached version.

Control flow, state, and persistence: The parent driver reads version information, sets up interrupt masking and domains, clears latched interrupts, and passes regmap access to child devices. Persistent state is PMIC register state; cached `ver` is live driver state used for variant behavior.

Dependencies and integration points: It depends on regmap and IRQ-domain infrastructure. It integrates with PMIC regulator, power key, thermal/fault, and platform child drivers that need the shared interrupt namespace.

Risks and test signals: Risks include stride/address confusion, failing to clear all four IRQ arrays, treating reserved interrupt bits as real signals, and version range checks that reject valid silicon. Test signals include IRQ domain mapping for 32 lines, status/mask/clear sequencing, version readback tests, and PMIC fault interrupt simulations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/hi655x-pmic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/idt82p33_reg.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/idt82p33_reg.h

Purpose: This header maps selected Renesas/IDT 82P33xxx Synchronization Management Unit registers used for DPLL, time-of-day, phase offset, holdover frequency, input mode, output muxing, and soft reset.

Important APIs, types, and constants: `REG_ADDR(page, offset)` composes paged register addresses. Register macros identify DPLL1/DPLL2 TOD config/status/trigger, operating mode/status, current frequency, phase offset, sync edge, input mode, holdover frequency, output mux config, and soft reset. Bit macros include `SYNC_TOD`, `PH_OFFSET_EN`, `SQUELCH_ENABLE`, PLL mode/combo fields, operating status fields, TOD trigger masks, and soft reset enable. Enums define PLL operating modes, hardware TOD trigger selections, and DPLL runtime states.

Control flow, state, and persistence: There are no functions. Consumers program DPLL mode, TOD trigger selection, phase/holdover data, and output squelch through lower-level I2C/SPI/regmap access. DPLL lock/holdover/freerun and TOD values are persistent hardware state while the device is powered.

Dependencies and integration points: It relies on `BIT()` from included context or other headers and integrates with PTP/timecard DPLL drivers that translate Linux PTP operations into register transactions.

Risks and test signals: Risks include paged-address composition errors, wrong read versus write TOD trigger nibble, mode values outside the enum range, and assuming DPLL1/DPLL2 symmetry where hardware differs. Test signals include TOD read/write trigger validation, PLL mode transition tests, DPLL state polling, output mux checks, and soft-reset recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/idt82p33_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/idt8a340_reg.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/idt8a340_reg.h

Purpose: This header maps a broad subset of Renesas/IDT 8A340 DPLL/timing-device registers. It is used by timing/PTP drivers to select pages, identify hardware/firmware revision, control DPLL TOD, synchronize output dividers, read DPLL/GPIO status, issue resets, and handle GPIO/TOD/clock-output routing.

Important APIs, types, and constants: Constants define global page address registers, hardware revision and DPLL base addresses, DPLL TOD control/override/output offsets, channel synchronization control registers, sync source IDs, sync trigger bits, Q8/Q11 special fanout and sync masks, reset commands, status block offsets, DPLL status registers, GPIO output/status registers, and many additional output, input, DPLL, TOD, and event status offsets through the file. The file is macro-only and uses register-block base plus offset patterns heavily.

Control flow, state, and persistence: Runtime flow in consumers uses the page selector to access 16-bit register windows, performs reset and sync-trigger writes, polls status, and reads or writes TOD/DPLL configuration. Persistent state is in DPLL lock/filter state, TOD counters, output divider sync setup, GPIO state, firmware revision fields, and NVM/OTP-selected product configuration.

Dependencies and integration points: It integrates with regmap or custom paged bus access, PTP clock drivers, DPLL state management, clock-output configuration, GPIO support, and board-specific synchronization routing.

Risks and test signals: Risks include page-register misuse, incomplete support for device version differences such as v5.20 reset/GPIO offsets, one-shot sync trigger bits left asserted, and mismatched output channel assumptions. Test signals include revision/product ID readback, reset command acceptance, DPLL lock status transitions, TOD capture/set tests, Q-channel sync tests, GPIO status/output tests, and PTP frequency/phase adjustment validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/idt8a340_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/idtRC38xxx_reg.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/idtRC38xxx_reg.h

Purpose: This file provides register definitions for Renesas/IDT RC38xxx timing hardware. It covers page addressing, DPLL/TOD register families, sync and output control, GPIO/status blocks, firmware/hardware IDs, and reset/status constants used by timing-card drivers.

Important APIs, types, and constants: The header is macro-only. It defines device identification and status offsets, DPLL base registers, time-of-day configuration/status/trigger fields, output mux and synchronization-related registers, reset controls, firmware version fields, and bit masks for DPLL operating state and trigger operations. The pattern mirrors the other IDT timing headers but targets the RC38xxx register layout.

Control flow, state, and persistence: Consumers perform paged register access, configure DPLL operating modes and TOD triggers, poll DPLL status, and route outputs/GPIOs. Hardware keeps persistent state for PLL lock/holdover, TOD counters, output divider configuration, reset state, and firmware identity.

Dependencies and integration points: It is consumed by PTP/time synchronization drivers and lower-level register access layers. It integrates with DPLL/PTP frameworks, clock-output configuration, and possibly GPIO/event reporting for timing cards.

Risks and test signals: Risks include mixing RC38xxx offsets with 82P33 or 8A340 layouts, using wrong page/offset calculations, and misinterpreting lock-state bitfields. Test signals include register identity readback, TOD trigger tests, DPLL mode/status polling, output mux validation, soft reset recovery, and cross-checking all masks against hardware programming guides.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/idtRC38xxx_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/imx25-tsadc.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/imx25-tsadc.h

Purpose: This header defines the Freescale i.MX25 touchscreen/ADC MFD shared register map. It describes the parent TSADC state, global control/status registers, queue register layout, FIFO/result extraction, interrupt/DMA masks, and per-item ADC configuration fields.

Important APIs, types, and constants: `struct mx25_tsadc` stores the regmap, IRQ domain, and clock. Register macros cover `MX25_TSC_TGCR`, `MX25_TSC_TGSR`, `MX25_TSC_TICR`, queue FIFO/control/status/mask/item/config registers, and channel-stride addressing. Bit macros configure power, reset, clock, sleep, ADC clock, internal reference, queue reset, watermark, repeat/fixed queue modes, FIFO status, DMA/IRQ enables, settling time, number of samples, touch-panel switch states, positive/negative references, input selection, and FIFO data/id extraction.

Control flow, state, and persistence: Parent code enables clocks and regmap, creates an IRQ domain, and child touchscreen/IIO ADC drivers program queue items and consume FIFO events. Runtime state includes queue configuration, FIFO contents, pending interrupts, ADC power mode, sampling references, and clock divider setup. Persistence is limited to hardware register state while powered.

Dependencies and integration points: It integrates with regmap, clk, IRQ domain, touchscreen input drivers, and IIO ADC consumers.

Risks and test signals: Risks include invalid `MX25_ADCQ_ITEM()` indexes, off-by-one sample count via `NOS(x)`, incorrect reference/input combinations damaging touch readings, and failing to clear FIFO errors. Test signals include pen/touch input tests, ADC channel readback, FIFO overrun/underrun handling, IRQ domain mapping, clock rate/divider validation, and suspend/resume power-mode checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/imx25-tsadc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/ingenic-tcu.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/ingenic-tcu.h

Purpose: This header maps the Ingenic JZ47xx Timer/Counter Unit registers shared by watchdog, clocksource/clockevent, and PWM users.

Important APIs, types, and constants: Register macros define watchdog timer data/control/count/CSR registers, global timer enable/status/flag/mask/stop registers, per-channel data-full/data-half/count/CSR registers, OST registers, and test registers. Field macros define parent clock selection, prescaler bits, PWM shutdown/initial-level/output-enable bits, watchdog enable, channel stride, and per-channel register address helpers `TCU_REG_TDFRc`, `TCU_REG_TDHRc`, `TCU_REG_TCNTc`, and `TCU_REG_TCSRc`.

Control flow, state, and persistence: There are no functions. Consumers enable/disable channels through global set/clear registers, program channel counters and compare values, and use CSR bits to select clock source/prescaler or PWM output behavior. State is hardware timer counts, flags, masks, enable bits, and watchdog state.

Dependencies and integration points: The header depends on bitops and integrates with Ingenic clocksource, clockevent, watchdog, PWM, and possibly regmap/syscon style access.

Risks and test signals: Risks include channel-stride mistakes, reserved CSR bits being overwritten, wrong parent clock selection, and watchdog enable sequencing. Test signals include timer interrupt accuracy, PWM duty/period tests, watchdog reset tests, channel enable/disable idempotence, and suspend/resume timer retention behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/ingenic-tcu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/intel-m10-bmc.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/intel-m10-bmc.h

Purpose: This is the shared header for Intel MAX 10 Board Management Controller MFD devices on FPGA cards. It defines CSR maps for N3000/N6000-like cards, secure update doorbell/status fields, flash access ranges and mux controls, platform information, flash bulk operations, firmware-update state, and parent device state.

Important APIs, types, and functions: Macros define system/flash memory ranges, staging area size, Nios firmware/build/MAC/telemetry offsets, RSU doorbell/auth result fields, RSU progress/status/host-state values, handshake and update timeouts, security image addresses and magic values, N6000 flash mux and FIFO controls, and flash polling timings. `struct m10bmc_csr_map` maps board-specific CSR offsets. `struct intel_m10bmc_platform_info` supplies MFD cells, handshake register ranges, and CSR map. `struct intel_m10bmc_flash_bulk_ops` abstracts flash read/write/lock/unlock. `enum m10bmc_fw_state` tracks normal and secure-update phases. `struct intel_m10bmc` stores device, regmap, platform info, optional flash ops, firmware state lock, and firmware state. Helpers include `m10bmc_raw_read`, `m10bmc_sys_read`, `m10bmc_sys_update_bits`, `m10bmc_fw_state_set`, and `m10bmc_dev_init`.

Control flow, state, and persistence: Core code initializes board-specific maps and children, reads system CSRs through regmap, coordinates RSU secure update by doorbell/host-status handshakes, arbitrates flash mux access, and tracks firmware state when direct handshakes are unavailable. Persistent state includes flash images, update counters, MAC addresses, telemetry counters, BMC firmware status, and RSU result fields.

Dependencies and integration points: It depends on bitfield/bits, regmap, rwsem, dev logging, MFD cells, and child drivers for secure update, HWMON, NVMEM, flash, and telemetry.

Risks and test signals: Risks include board map mismatch, long timeout paths blocking update flows, flash write without lock, read returning `-EBUSY` during locked writes, stale firmware state after failed update, and incorrect interpretation of doorbell fields. Test signals include CSR map readback, RSU state-machine tests, flash mux contention tests, secure-update timeout/error injection, telemetry child reads, and rwsem/lockdep coverage around firmware state changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/intel-m10-bmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/intel_pmc_bxt.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/intel_pmc_bxt.h

Purpose: This header exposes the Intel Broxton PMC MFD interface for global configuration register access and S0ix telemetry.

Important APIs, types, and functions: Register macros define PMC GCR configuration, deep S0ix telemetry, and shallow S0ix telemetry offsets. `PMC_CFG_NO_REBOOT_EN` identifies the no-reboot bit. `struct intel_pmc_dev` stores the parent device, SCU IPC device, MMIO base for GCR registers, spinlock for GCR serialization, and optional telemetry SSRAM resource. If `CONFIG_MFD_INTEL_PMC_BXT` is enabled, exported helpers read 64-bit GCR values, update GCR bitfields, and read S0ix counters; otherwise inline stubs return `-ENOTSUPP`.

Control flow, state, and persistence: Consumers call helper functions to serialize register updates under `gcr_lock` and read telemetry. Persistent hardware state includes PMC config bits and telemetry counters; the struct tracks live mapping and IPC dependencies.

Dependencies and integration points: It integrates with Intel SCU IPC, PMC platform code, power management telemetry, and drivers that need no-reboot or S0ix information.

Risks and test signals: Risks include using helpers when the config is disabled, missing spinlock protection for GCR access, wrong telemetry resource mapping, and confusing shallow/deep S0ix counters. Test signals include compile coverage with PMC enabled and disabled, GCR update readback, S0ix counter reads across suspend cycles, and lockdep around concurrent GCR updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/intel_pmc_bxt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/intel_soc_pmic.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/intel_soc_pmic.h

Purpose: This header defines the common Intel SoC PMIC parent state and helper for executing MIPI PMIC sequence elements. It is shared by Cherry Trail/Whiskey Cove/Basin Cove style PMIC code and child IRQ domains.

Important APIs, types, and functions: `enum intel_cht_wc_models` identifies several Cherry Trail Whiskey Cove board quirks. `struct intel_soc_pmic` stores the master IRQ, regmap, primary and chained regmap IRQ chip data for power button, TMU, BCU, ADC, charger, critical event, device pointer, SCU IPC handle, and board model. `intel_soc_pmic_exec_mipi_pmic_seq_element` applies a register write/masked update described by firmware/MIPI sequence data.

Control flow, state, and persistence: The parent PMIC driver sets up regmap and nested IRQ chips, detects board model quirks, and child drivers use the shared regmap/IRQ data. Firmware sequence execution writes PMIC registers through an I2C address/register/mask/value tuple. State is in PMIC registers, nested IRQ masks/status, and board quirk selection.

Dependencies and integration points: It depends on regmap and Intel SCU IPC. It integrates with ACPI-described PMIC children, power button, thermal, charger, ADC, BCU, GPIO, and regulator drivers.

Risks and test signals: Risks include nested IRQ chip mismatch, board quirk misdetection, executing firmware sequence writes on the wrong I2C address, and mask/value ordering bugs. Test signals include IRQ tree tests, ACPI sequence replay tests, board-specific quirk probes, charger/ADC interrupt tests, and regmap trace verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/intel_soc_pmic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/intel_soc_pmic_bxtwc.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/intel_soc_pmic_bxtwc.h

Purpose: This header maps Intel Broxton Whiskey Cove PMIC device addresses and selected charger, USB, wake, and thermal registers.

Important APIs, types, and constants: It defines three PMIC I2C device addresses and combined address/register macros for chip ID/version, charger IRQ/control/status, battery thermal zone, USB path/PHY/ID/source-detect/debug registers, wake-source registers, charger RTT address/data, and thermal interrupt/zone high/low registers. `BXTWC_USBIDEN_MASK` identifies USB-ID enable.

Control flow, state, and persistence: There is no code. Consumers use these constants with the common Intel SoC PMIC regmap/SCU access path to configure USB/charger/thermal behavior and decode wake sources. State persists in PMIC registers and interrupt latches.

Dependencies and integration points: It integrates with Intel SoC PMIC core, charger/power-supply drivers, USB role/source detection, thermal zones, and wakeup handling.

Risks and test signals: Risks include wrong combined device/register addressing, overlapping status aliases such as charger status and USB path at the same address, and thermal-zone register pair ordering errors. Test signals include charger attach/detach IRQs, USB ID/source detection, wake-source readback, thermal threshold tests, and chip ID/version probe checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/intel_soc_pmic_bxtwc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/intel_soc_pmic_mrfld.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/intel_soc_pmic_mrfld.h

Purpose: This header defines Intel Merrifield Basin Cove PMIC ID, interrupt, mask, and level-two IRQ bitfields for the common Intel SoC PMIC stack.

Important APIs, types, and constants: Register macros identify ID, level-one IRQ, power-button, TMU, thermal, BCU, ADC, charger, GPIO, critical, and corresponding mask registers. ID extraction helpers `BCOVE_MINOR`, `BCOVE_MAJOR`, and `BCOVE_VENDOR` decode revision/vendor fields. Level-one bits identify the IRQ groups, and level-two bits cover power button press/release, ADC events, charger battery alerts, VBUS/DC/battery/USB-ID detection, and critical charger conditions.

Control flow, state, and persistence: Consumers read interrupt status groups, mask/unmask nested IRQs, and decode PMIC revision. State is PMIC interrupt latch/mask state and hardware revision data.

Dependencies and integration points: It depends on `linux/bits.h` and integrates with `intel_soc_pmic.h`, regmap-irq, power button, ADC, charger, GPIO, thermal, and critical-event child drivers.

Risks and test signals: Risks include grouped IRQ masking errors, charger IRQ0/IRQ1 confusion, ID field decoding mistakes, and missing critical-event handling. Test signals include nested IRQ group tests, charger detection interrupts, ADC interrupt tests, ID decode validation, and suspend wakeup from power button or charger insertion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/intel_soc_pmic_mrfld.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/ipaq-micro.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/ipaq-micro.h

Purpose: This header defines the Compaq iPAQ microcontroller MFD protocol and parent state. It models the serial packet parser, transmit queue, message format, synchronous/asynchronous message helpers, and callbacks for keyboard and touchscreen events.

Important APIs, types, and functions: Message IDs cover version, keyboard, touchscreen, EEPROM, thermal sensor, LEDs, battery, SPI, backlight, codec, and display control. `enum rx_state` models SOF, ID, data, and checksum parser states. `struct ipaq_micro_txdev` and `struct ipaq_micro_rxdev` hold ISR transmit/receive parser state. `struct ipaq_micro_msg` stores command ID, TX/RX buffers, completion, and queue node. `struct ipaq_micro` stores MMIO bases, version, TX/RX state, spinlock, active message, queue, and async key/touch callbacks. `ipaq_micro_tx_msg` is exported; inline `ipaq_micro_tx_msg_sync` initializes completion, sends, and waits, while `ipaq_micro_tx_msg_async` sends without waiting.

Control flow, state, and persistence: TX messages are queued and emitted through interrupt-driven serial state; RX bytes advance the parser state machine and complete the matching message or dispatch async key/touch callbacks. Driver state is queue, current message, parser indices, checksum, and callbacks. Persistent device state includes microcontroller firmware behavior and EEPROM contents.

Dependencies and integration points: It depends on spinlocks, completions, and lists. It integrates with platform children for battery, LEDs/backlight, input keyboard/touchscreen, thermal, EEPROM, SPI, and legacy audio/display controls.

Risks and test signals: Risks include waiting forever in `ipaq_micro_tx_msg_sync` if no completion occurs, buffer length overruns, checksum/parser resync bugs, callback lifetime issues, and locking mistakes in ISR context. Test signals include malformed packet parser tests, TX queue ordering, timeout coverage in callers, async key/touch event delivery, EEPROM read/write, and suspend/resume serial recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/ipaq-micro.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/iqs62x.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/iqs62x.h

Purpose: This header defines the Azoteq IQS620/621/622/624/625 multifunction sensor core interface. It captures product/hardware IDs, event register layout, event descriptors, per-device descriptors, and shared core state for proximity, SAR, hall, ALS/IR, wheel, and PMU-style children.

Important APIs, types, and constants: Constants define product numbers, IQS620 hardware revisions, ALS flag register addresses, IQS624 hall UI register and bits, global event mask, key/event counts, and event table width. Enums define UI selection, event-register groups, and event flags for key-like and switch-like events. `struct iqs62x_event_data` carries decoded UI and ALS flags. `struct iqs62x_event_desc` maps event flags to register/bit metadata. `struct iqs62x_dev_desc` describes each chip variant, subdevices, calibration registers, masks, flags, firmware name, and event register matrix. `struct iqs62x_core` stores descriptor, I2C client, regmap, blocking notifier, firmware block list, ATI/firmware completions, selected UI, event cache, and hardware/software numbers. `iqs62x_events` exports the global event descriptor table.

Control flow, state, and persistence: The core probes the chip, selects a descriptor by product/hardware/software number, optionally loads firmware/calibration, registers MFD subdevices, masks/unmasks global events, caches event bits, and notifies children. Persistent state includes sensor calibration and firmware behavior; live kernel state includes notifier subscribers, firmware blocks, completions, selected UI, and event cache.

Dependencies and integration points: It integrates with I2C/regmap, MFD cells, firmware loading, notifier chains, completions, input, IIO/ALS, hall sensor, and power management children.

Risks and test signals: Risks include descriptor mismatch across similar products, notifier ordering bugs, stale `event_cache`, firmware completion timeouts, and event matrix width mismatches. Test signals include product ID probe tests, ATI/firmware completion handling, event notification for all `IQS62X_NUM_EVENTS`, suspend/resume event mask restore, and child-driver calibration reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/iqs62x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/janz.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/janz.h

Purpose: This header defines common data structures for Janz MODULbus devices, especially the CMOD-IO onboard PLX bridge register layout and platform module number.

Important APIs, types, and constants: `struct janz_platform_data` carries the MODULbus module number. `struct janz_cmodio_onboard_regs` maps byte-wide onboard registers with padding bytes, including interrupt disable/status, interrupt enable/module-number, reset assert/deassert, serial EEPROM data, and EEPROM chip select.

Control flow, state, and persistence: There is no code. Drivers memory-map the PLX bridge and read/write these byte registers to enable/disable interrupts, assert/deassert reset, identify the module switch value, and access EEPROM. Persistent state may exist in the EEPROM and physical module number switch; interrupt/reset registers are live hardware state.

Dependencies and integration points: It integrates with PCI or platform code for Janz MODULbus carriers and child device registration for modules.

Risks and test signals: Risks include struct layout/padding assumptions against MMIO hardware, read/write semantics changing by access direction, reset sequencing mistakes, and EEPROM chip-select misuse. Test signals include compile-time layout review, interrupt enable/disable tests, reset toggling, module-number readback, and EEPROM read/write validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/janz.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/kempld.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/kempld.h

Purpose: This header defines the Kontron PLD MFD register interface, device information structures, platform callbacks, and indexed I/O access helpers.

Important APIs, types, and functions: Constants define index/data I/O ports, mutex key, version/build/feature/spec registers, feature bits, IRQ/GPIO/I2C config, PLD clock, type values, and version string length. `struct kempld_info` stores parsed revision/build/type/spec/version data. `struct kempld_device_data` stores mapped I/O base/index/data, clock, feature mask, device, info, and mutex. `struct kempld_platform_data` supplies clock, GPIO base, I/O resource, hardware mutex callbacks, info callback, and cell registration callback. Exported helpers acquire/release the PLD mutex and read/write 8/16/32-bit indexed registers.

Control flow, state, and persistence: Parent code probes the indexed I/O region, parses version and feature registers, optionally uses hardware mutex callbacks, registers child cells, and serializes all indexed access. Persistent state includes PLD firmware version, feature bits, BIOS write-protect/config bits, watchdog/GPIO/I2C hardware state, and board-specific callbacks.

Dependencies and integration points: It integrates with MFD child registration for GPIO, I2C, watchdog, and possibly NMI/SMI/SCI signaling. It depends on resources, mutexes, MMIO/I/O access, and board platform data.

Risks and test signals: Risks include failing to serialize index/data accesses, wrong endian/width handling for 16/32-bit helpers, feature-mask misinterpretation, and platform callbacks not honoring hardware mutex semantics. Test signals include concurrent read/write stress, version parsing tests, feature-driven child registration, GPIO/I2C/watchdog child probes, and BIOS write-protect config readback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/kempld.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/khadas-mcu.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/khadas-mcu.h

Purpose: This header maps the Khadas system-control MCU register space and parent state. It covers vendor/user passwords, MAC/USID/version/device identifiers, boot and wake controls, LEDs, shutdown, IR, USB/PCIe switching, user data, power-off and password commands, WOL/fan commands, and board IDs.

Important APIs, types, and constants: Register macros define read-only identity fields, read/write boot/wakeup/LED/shutdown/MAC/IR/sleep/switch/password/user-data registers, write-only command registers, and read-only shutdown status. The enum identifies VIM1, VIM2, VIM3, Edge, and Edge-V board IDs. `struct khadas_mcu` stores device and regmap pointers.

Control flow, state, and persistence: Consumers read identity/version data, configure wake sources and boot modes, update LED or fan controls, issue power-off/password/WOL commands, and access user data through regmap. Persistent state includes MCU NVM/user data, passwords, MAC address, wake policy, and boot settings.

Dependencies and integration points: It integrates with regmap-backed I2C MCU access, poweroff/reboot handlers, NVMEM/MAC providers, LED drivers, fan/hwmon support, wakeup sources, and board-detection code.

Risks and test signals: Risks include writing command-only registers accidentally, exposing or corrupting password/user-data fields, wrong board ID mapping, and wake-source settings persisting unexpectedly. Test signals include identity readback, boot/wake setting round trips, poweroff command path, LED/fan command tests, MAC/NVMEM reads, and suspend wakeup validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/khadas-mcu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/lm3533.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/lm3533.h

Purpose: This header defines the TI LM3533 lighting MFD interface. It shares parent state, control-bank state, platform data for ALS/backlights/LEDs, boost configuration enums, sysfs attribute helpers, and register access/control-bank helpers.

Important APIs, types, and functions: `LM3533_ATTR_RO` and `LM3533_ATTR_RW` create device attributes. `struct lm3533` stores device, regmap, hardware-enable GPIO, IRQ, and feature flags for ALS/backlights/LEDs. `struct lm3533_ctrlbank` identifies a logical current/brightness control bank. Platform data structures describe ALS PWM/resistor selection, backlight names/current/default brightness/PWM, LED names/triggers/current/PWM, and global boost OVP/frequency. Exported helpers enable/disable control banks, set/get brightness, set max current, set/get PWM, and perform read/write/update register operations.

Control flow, state, and persistence: The parent driver controls hardware-enable GPIO, initializes regmap and child devices based on platform data, and children call control-bank helpers to update brightness/current/PWM fields. Persistent state is in LM3533 registers and LED/backlight output configuration; live state includes feature flags and child control-bank IDs.

Dependencies and integration points: It integrates with regmap, GPIO descriptors, LED class, backlight subsystem, ALS input/IIO-style consumers, IRQ handling, and sysfs attributes.

Risks and test signals: Risks include invalid current/PWM ranges, control-bank ID mismatch, concurrent updates to shared regmap fields, and sysfs permission macro drift. Test signals include LED/backlight brightness tests, max-current validation, hardware-enable GPIO sequencing, ALS mode tests, IRQ behavior, and regmap update-bit traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/lm3533.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/lochnagar.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/lochnagar.h

Purpose: This header defines the shared Cirrus Logic Lochnagar audio board MFD core data and common base registers. It supports Lochnagar1 and Lochnagar2 devices and provides the analogue configuration update entry point.

Important APIs, types, and functions: `enum lochnagar_type` distinguishes `LOCHNAGAR1` and `LOCHNAGAR2`. `struct lochnagar` stores the board type, parent device, regmap, and `analogue_config_lock`. Common register macros cover software reset and firmware ID registers plus device and revision ID masks/shifts. `lochnagar_update_config` is exported to apply pending analogue configuration updates.

Control flow, state, and persistence: Consumers update regmap fields for clocks, audio routing, GPIOs, regulators, or analogue paths, then call `lochnagar_update_config` for hardware that latches analogue changes. The mutex protects updates while hardware processes the previous analogue update. Persistent state is board register configuration and firmware identity.

Dependencies and integration points: It depends on device, mutex, and regmap infrastructure. It integrates with `lochnagar1_regs.h`, `lochnagar2_regs.h`, audio clock/routing drivers, regulators, GPIO, and board MFD child devices.

Risks and test signals: Risks include missing the analogue update/latch step, failing to hold the lock around related analogue changes, and using Lochnagar1 register definitions on Lochnagar2. Test signals include device/revision ID reads, concurrent analogue update tests, audio route changes, regulator/GPIO child probes, and reset recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/lochnagar.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/lochnagar1_regs.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/lochnagar1_regs.h

Purpose: This header defines Lochnagar1 board register addresses and bitfields for audio interface routing, MCLK selection, DSP/codec clocks, general-purpose audio interfaces, GPIO/LED, reset, and I2C codec interface mode.

Important APIs, types, and constants: Register macros include codec AIF selections, codec MCLK selections, AIF control registers, external AIF control, DSP AIF and clock selection, GF/PSIA/SPDIF routing, GPIO/LED registers, reset, and I2C control. Bitfields define common source selection, LRCLK/BCLK direction, AIF enable bits, MCLK enable bits, GF clock output enable, DSP and codec reset bits, and codec CIF mode.

Control flow, state, and persistence: There is no code. Consumers write source-select fields and enable/direction bits to route clocks and serial audio between codecs, DSP, PSIA, SPDIF, and general-function headers. Reset bits control attached codec/DSP devices. State is board routing and reset configuration persisted in Lochnagar1 registers while powered.

Dependencies and integration points: It integrates with the Lochnagar core regmap, ALSA SoC machine/card support, clock framework consumers, GPIO/LED children, and board reset control.

Risks and test signals: Risks include source-route mismatches, wrong LRCLK/BCLK master direction, forgetting to enable an AIF/MCLK after selecting a source, and reset polarity misuse. Test signals include audio loopback on each routed AIF, MCLK frequency/enable checks, DSP/codec reset tests, LED/GPIO register tests, and I2C CIF mode readback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/lochnagar1_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/lochnagar2_regs.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/lochnagar2_regs.h

Purpose: This header defines the larger Lochnagar2 register map. It covers audio interface and clock routing, GPIO and GPIO-channel routing, reset controls, analogue path update controls, mic-bias and regulator fields, SPDIF, current monitor, power control, and codec core voltage settings.

Important APIs, types, and constants: Register macros cover many Lochnagar2 routing/control blocks. Key bitfields include AIF enable/LRCLK/BCLK/source masks, clock enable/source masks, GPIO source and channel source/status masks, DSP and codec reset bits, analogue path update and update status bits, input-bias and mic-bias source fields, codec CIF mode, SPDIF reset/hardware mode, IMON enable/channel/data-ready/data masks, power enable, MICVDD regulator enable/voltage select, and VDDCORE codec regulator enable/voltage select.

Control flow, state, and persistence: Consumers program routing and regulator fields through regmap. Analogue path changes require update sequencing coordinated with `lochnagar_update_config` and the core lock. IMON measurement flow configures channels, triggers measurement/data request, and polls done/data-ready bits. Hardware register state persists board routing, resets, regulator settings, and monitor configuration.

Dependencies and integration points: It integrates with the Lochnagar core, ALSA SoC audio routing/clocking, GPIO, regulator, SPDIF, and current-monitor consumers.

Risks and test signals: Risks include leaving one-shot analogue or IMON trigger bits asserted, mismatching GPIO channel status/source fields, wrong regulator voltage select masks, and missing reset sequencing for attached audio devices. Test signals include AIF routing tests, analogue path latch tests, IMON measurement readback, regulator enable/voltage tests, GPIO channel routing, and SPDIF reset/mode validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/lochnagar2_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/loongson-se.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/loongson-se.h

Purpose: This header defines the Loongson Security Engine MFD interface for controller commands, interrupts, engine IDs, command sizes, and per-engine runtime state.

Important APIs, types, and functions: Macros define controller command timeout, command registers, command IDs for start/DMA/engine command buffer setup, interrupt status/enable/clear/set registers, all/controller interrupt masks, maximum engine count, RNG and TPM engine IDs and command bases, and command buffer size. `struct loongson_se_engine` stores the parent security engine pointer, engine ID, command and return buffers, data buffer, buffer size and DMA-base offset, and completion. Exported functions are `loongson_se_init_engine` and `loongson_se_send_engine_cmd`.

Control flow, state, and persistence: Consumers initialize a selected engine, prepare command/data buffers, send an engine command through controller registers, and wait on completion signaled by interrupts. State includes DMA command/data buffers, per-engine completion, interrupt status, and engine command return contents.

Dependencies and integration points: It integrates with Loongson SE parent code, DMA-capable buffers, completion/interrupt handling, RNG and TPM child drivers, and MMIO register access.

Risks and test signals: Risks include command timeout, DMA offset/size mismatch, completion not firing on interrupt loss, command buffer alignment assumptions, and engine ID misuse. Test signals include RNG command smoke tests, TPM command exchange, interrupt clear/enable tests, timeout/error injection, and DMA buffer boundary checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/loongson-se.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/lp3943.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/lp3943.h

Purpose: This header defines the TI/National LP3943 MFD interface for a 16-output GPIO/PWM/LED expander. It maps registers, output mux states, PWM output IDs, platform mappings, parent state, and regmap byte helpers.

Important APIs, types, and functions: Register macros cover GPIO A/B, two prescalers, two PWM duty registers, and four mux registers. Mux constants select input, output high/low, dim via PWM0, or dim via PWM1. `enum lp3943_pwm_output` names 16 outputs. `struct lp3943_pwm_map` maps outputs to a PWM channel. `struct lp3943_platform_data` provides the two PWM mappings. `struct lp3943_reg_cfg` describes register/mask/shift for a pin. `struct lp3943` stores device, regmap, platform data, mux config table, and `pin_used` bitmap. Helpers perform byte read/write/update.

Control flow, state, and persistence: The parent initializes regmap and mux configuration, then GPIO/PWM/LED children claim pins using `pin_used` and update mux/PWM/prescaler registers. Hardware state includes pin mux modes, output levels, PWM period/duty, and GPIO input state.

Dependencies and integration points: It depends on GPIO and regmap and integrates with GPIO, PWM, and LED child drivers.

Risks and test signals: Risks include pin allocation races, overlapping PWM and GPIO use, incorrect mux mask/shift for an output, and platform data mapping invalid outputs. Test signals include GPIO input/output tests for all 16 pins, PWM channel mapping tests, LED dimming tests, concurrent pin claim tests, and regmap update-bit traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/lp3943.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/lp873x.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/lp873x.h

Purpose: This header defines the TI LP873x PMIC shared register map and parent state. It covers two buck regulators, two LDOs, GPOs, startup/shutdown delays, configuration, PLL, power-good, interrupts, status, masks, load-current measurement, and regulator IDs.

Important APIs, types, and constants: Register macros define device/OTP revision, buck/LDO control and voltage registers, delay registers, GPO control/delay, config, PLL, PGOOD controls, fault/reset, interrupt/status/mask blocks, and load-current registers. Field macros cover regulator enables, pin control, discharge, FPWM, current limit, slew rate, voltage set masks, delay nibbles, GPO open-drain/enables, config bits, PLL frequency, power-good selection, interrupt/status bits, and masks. `enum lp873x_regulator_id` names two bucks and two LDOs. `struct lp873x` stores device, revision, and regmap.

Control flow, state, and persistence: The MFD core probes revision, initializes regmap and IRQs, and regulator/GPO children update control, voltage, delay, and mask registers. Runtime state includes regulator enable/voltage, interrupt latches, power-good/fault state, and load-current selection/results. Settings persist in PMIC registers while powered and may be influenced by OTP.

Dependencies and integration points: It depends on I2C and regulator headers and integrates with regmap/regulator/IRQ/power-good handling.

Risks and test signals: Risks include confusing buck/LDO status and mask bits, programming delay nibbles incorrectly, load-current selection races, and assuming one LP873x OTP layout. Test signals include regulator voltage/enable tests, interrupt mask/status tests, power-good fault injection, GPO control tests, revision readback, and load-current read sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/lp873x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/lp87565.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/lp87565.h

Purpose: This header defines the TI LP87565/LP87524/LP87561 PMIC shared register map and parent state. It focuses on four buck regulators, floor/roof voltage support, GPIOs, power-good, PLL, interrupt/status/mask blocks, load-current measurement, and variant IDs.

Important APIs, types, and constants: `enum lp87565_device_type` distinguishes supported variants. Register macros cover device/OTP revision, four buck control and voltage/floor registers, buck and GPIO delays, reset/config, top and buck interrupts/status/masks, load-current, PGOOD, PLL, pin function, GPIO config/in/out, and max register. Field macros cover buck enable/pin select/roof-floor/discharge/FPWM/current limit/slew/voltage, delay nibbles, reset/config bits, top and buck interrupt/status/mask bits, load-current selection/results, PGOOD selection and fault bits, PLL mode/frequency, pin-function selection, GPIO open-drain/direction/input/output, and spread spectrum. `struct lp87565` stores device, revision, device type, regmap, and optional reset GPIO.

Control flow, state, and persistence: The parent detects variant/revision, initializes regmap and children, may use reset GPIO, and child regulator/GPIO/IRQ code programs buck, PGOOD, load-current, and GPIO fields. Runtime state includes regulator mode/voltage/floor, IRQ latches, GPIO state, power-good configuration, and OTP-determined variant behavior.

Dependencies and integration points: It depends on I2C, regulator, GPIO descriptor through users, and regmap. It integrates with regulator, GPIO, IRQ, reset, power-good, and board PMIC configuration.

Risks and test signals: Risks include variant-specific buck count/behavior mismatch, typo-prone `LPL87565_*` mask names, bit0 FPWM limitation for only BUCK0/BUCK2, reset GPIO sequencing, and power-good mask confusion. Test signals include variant probe tests, all buck voltage/mode tests, floor/roof behavior, IRQ/status/mask tests, GPIO direction/value tests, PGOOD fault tests, reset GPIO tests, and load-current measurement sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/lp87565.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/lp8788-isink.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/lp8788-isink.h

Purpose: This header defines current-sink register addresses and masks for the TI LP8788 MFD, typically used by LED/backlight current-sink child drivers.

Important APIs, types, and constants: Register macros identify current-sink control, ISINK1/2 output current, ISINK3 output current, and PWM registers for three sinks. Masks define output-current fields for ISINK1, ISINK2, and ISINK3. `LP8788_ISINK_MAX_PWM` bounds PWM value to 63, and `LP8788_ISINK_SCALE_OFFSET` describes scaling/shift behavior used by consumers.

Control flow, state, and persistence: There is no code. Child drivers program current and PWM registers through the LP8788 parent regmap to enable and dim current sinks. Hardware state is current limit/output and PWM duty configuration.

Dependencies and integration points: It integrates with the LP8788 MFD core, regmap, LED class, and backlight drivers.

Risks and test signals: Risks include nibble-mask mistakes for shared ISINK1/2 current register, accepting PWM values above 63, and mismatched scaling in brightness conversions. Test signals include LED brightness ramp tests, current setting readback, shared-register update-bit tests for ISINK1/2, and suspend/resume brightness restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/lp8788-isink.h -->
