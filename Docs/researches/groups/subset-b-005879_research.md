# subset-b-005879 Research

Grouped research for Linux MFD-facing headers under `sources/distributed-fs/ceph-client/include/linux/mfd`. Each section is marker-delimited for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/mt6357/registers.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/mt6357/registers.h

## Purpose

This 1574-line header is the MT6357 PMIC register map. It assigns symbolic names to 16-bit register addresses across the chip's top, GPIO, clock/reset, SPI wrapper, RTC, DCXO, charger/startup, battery monitor, fuel gauge, AUXADC, buck regulator, LDO, LED/current-sink, audio, and accessory-detection blocks. It is a compile-time hardware contract: drivers include it so that regmap reads/writes refer to named MT6357 addresses rather than raw offsets.

## Important APIs, Types, and Functions

The file exports no functions or types. Its API surface is the `MT6357_*` macro namespace. Important groups include chip identity/status registers such as `MT6357_SWCID`, interrupt controller registers such as `MT6357_TOP_INT_STATUS0`, `MT6357_PSC_TOP_INT_CON0`, `MT6357_BM_TOP_INT_STATUS0`, `MT6357_BUCK_TOP_INT_CON0`, `MT6357_LDO_TOP_INT_STATUS0`, and `MT6357_AUD_TOP_INT_STATUS0`, RTC registers from `MT6357_RTC_BBPU` through secure RTC offsets, AUXADC request/status/result registers, regulator control/debug/ELR addresses for buck and LDO supplies, and audio/accessory detection register names.

## Control Flow

There is no executable flow in this header. Runtime flow appears in consumers: `drivers/mfd/mt6397-core.c` uses identity and RTC-related constants while instantiating MFD cells, `drivers/mfd/mt6358-irq.c` uses MT6357 top interrupt register addresses with the shared PMIC IRQ code path, `drivers/regulator/mt6357-regulator.c` maps regulator descriptors to these addresses, `drivers/input/keyboard/mtk-pmic-keys.c` uses power/home key status addresses, and sound codec/accessory drivers use the audio/ACCDET regions.

## State and Persistence Behavior

The file owns no storage. The named addresses target persistent PMIC hardware state: power/reset status, RTC counters/alarm registers, EFUSE/ELR trim values, regulator enable and voltage selection state, interrupt latches and masks, and analog monitor/debug values. Register writes can survive until PMIC reset or, for RTC/backup domains, across AP power transitions depending on the hardware domain.

## Dependencies and Integration Points

The only dependency is the include guard. Integration is through Linux regmap and MFD children below the MT6397-family core. The address map must stay consistent with MT6357 silicon and with companion headers such as `mt6357/core.h`, because IRQ numbers and MFD resources point at these register blocks by name. Regulator, input, RTC, AUXADC, and sound drivers depend on these constants being correct for their bitfield definitions.

## Risks and Edge Cases

The main risk is silent hardware misprogramming from a wrong offset or an MT6358/MT6359 address being reused for MT6357 where banks differ. Long contiguous macro lists also invite copy/paste drift in `_SET` and `_CLR` aliases. RTC and regulator addresses are particularly sensitive because they affect persistent power state. Interrupt status and mask register mistakes can lose wake events or leave storming IRQ lines. There is no type checking around macro use, so cross-chip misuse compiles.

## Test Signals

Useful signals are build coverage for `mt6397-core`, `mt6358-irq`, `mt6357-regulator`, PMIC key, RTC, AUXADC, and sound codec consumers; boot probing on MT6357 hardware; regmap debugfs spot checks for known chip ID/status addresses; regulator enable/voltage smoke tests; PMIC key IRQ tests; RTC read/set/alarm tests; and suspend/resume wake tests that exercise masked and latched interrupt registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/mt6357/registers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/mt6358/core.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/mt6358/core.h

## Purpose

This header defines the MT6358 PMIC interrupt topology contract shared by the MT6397-family MFD core and the `mt6358-irq` implementation. It describes how top-level PMIC interrupt groups map to Linux hardware IRQ numbers and how enable/status registers are generated for each group.

## Important APIs, Types, and Functions

`struct irq_top_t` describes one PMIC interrupt top block with a hardware IRQ base, number of interrupt status registers, enable/status register addresses, shifts between adjacent registers, and the bit offset in the top status register. `struct pmic_irq_data` aggregates all top blocks, the total IRQ count, top status register address, and enable/cache bit arrays. `enum mt6358_irq_top_status_shift` names the top status bits: buck, LDO, PSC, SCK, BM, HK, AUD, and MISC. `enum mt6358_irq_numbers` assigns stable hwirq numbers for regulator over-current, keys, charger, RTC, battery/fuel-gauge, audio/accessory, and SPI alert events. `MT6358_IRQ_*_BASE`, `MT6358_IRQ_*_BITS`, and `MT6358_TOP_GEN(sp)` are macro helpers used to build the top-block table.

## Control Flow

The header has no runtime flow itself. In the IRQ driver, a table built with `MT6358_TOP_GEN(BUCK)` and related groups lets the handler read `top_int_status_reg`, identify asserted top groups, then iterate per-group status registers. Enable/disable paths use `en_reg` plus `en_reg_shift` and cached hwirq booleans to update hardware masks while preserving other PMIC IRQ state.

## State and Persistence Behavior

The structs describe driver-owned runtime state, not persistent storage. `enable_hwirq` and `cache_hwirq` are in-memory bit arrays used to synchronize Linux IRQ state with PMIC enable registers. Actual event latches and mask state live in the PMIC registers named by `mt6358/registers.h` and persist until cleared or reset by hardware/driver flow.

## Dependencies and Integration Points

The macros expect `MTK_PMIC_REG_WIDTH` and register constants such as `MT6358_BUCK_TOP_INT_CON0` to be visible from companion includes in `drivers/mfd/mt6358-irq.c`. The MFD core calls `mt6358_irq_init()` for MT6357, MT6358, and MT6359-like devices, so the topology shape must align with each chip-specific core header and register map. MFD child resources in `mt6397-core.c` refer to hwirq constants such as `MT6358_IRQ_RTC` and key IRQs.

## Risks and Edge Cases

Numbering holes in `enum mt6358_irq_numbers` are intentional because hardware groups are register-aligned; collapsing or reordering them would break resource mappings. `MT6358_TOP_GEN()` assumes fixed register spacing (`0x6` enable, `0x2` status) and a common register width, so any top block with different spacing must not use it unchanged. Off-by-one errors in `*_BITS` change the number of scanned registers and can hide high IRQ bits.

## Test Signals

Compile `drivers/mfd/mt6358-irq.c` with MT6358 enabled, boot an MT6358 platform, verify MFD child resources resolve expected Linux IRQs for RTC and PMIC keys, exercise key press/release, charger detect, RTC alarm, and regulator over-current paths, and inspect `/proc/interrupts` or irqdomain mappings for stable hwirq numbers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/mt6358/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/mt6358/registers.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/mt6358/registers.h

## Purpose

This header is the MT6358 PMIC register-address contract. It is narrower than the full MT6357 map but covers the addresses used by Linux consumers: chip ID/status, top interrupt registers, RTC and secure RTC blocks, PSC/BM/HK interrupt blocks, buck and LDO regulator blocks, analog regulator monitor blocks, and audio interrupt registers.

## Important APIs, Types, and Functions

The file exports only `MT6358_*` macros. Important definitions include `MT6358_SWCID`, `MT6358_TOP_INT_STATUS0`, `MT6358_MISC_TOP_INT_CON0`, `MT6358_SCK_TOP_INT_CON0`, RTC addresses from `MT6358_RTC_BBPU` to `MT6358_RTC_SEC_WRTGR`, IRQ top registers for PSC/BM/HK/BUCK/LDO/AUD, individual buck register blocks such as `MT6358_BUCK_VPROC11_CON0` and `MT6358_BUCK_VCORE_ELR0`, LDO blocks such as `MT6358_LDO_VXO22_CON0`, `MT6358_LDO_VSRAM_PROC11_DBG0`, and aliases for MT6366-compatible regulator naming.

## Control Flow

No executable flow is present. Runtime drivers use the constants in regmap transactions. `mt6397-core.c` reads `MT6358_SWCID` and registers RTC/key child devices. `mt6358-irq.c` combines these addresses with `MT6358_TOP_GEN()` for hierarchical IRQ handling. `mt6358-regulator.c` uses the regulator and analog monitor addresses to implement enable, voltage selection, mode, and status operations.

## State and Persistence Behavior

The file maps hardware state but owns none. PMIC state includes latched interrupt bits, RTC time/alarm/power-down data, regulator enable and voltage state, debug monitor values, and analog trim/ELR values. Writes to regulator and RTC registers can change platform power behavior until later driver action or hardware reset.

## Dependencies and Integration Points

The header is consumed with `mt6358/core.h` by the shared IRQ code, with `mt6397/core.h` by MFD children, and by MT6358/MT6366 regulator descriptors. It depends on convention more than C types: suffixes like `_CON0`, `_DBG0`, `_ELR0`, `_ANA_CON0`, `_INT_CON0`, and `_INT_STATUS0` must match macro construction and driver descriptor expectations.

## Risks and Edge Cases

Cross-chip aliasing is a real risk: MT6358 and MT6366 share driver paths but do not expose identical regulators, so the MT6366 aliases must point at intentionally reused address slots. Incorrect RTC base offsets or write-trigger addresses break time/alarm updates. Regulator descriptor masks are defined elsewhere, so a correct address with a wrong companion mask can still misprogram voltage or mode.

## Test Signals

Build MT6358 MFD, IRQ, RTC, keyboard, and regulator drivers; boot on MT6358/MT6366 hardware; verify `SWCID`; list regulators from debugfs/sysfs; test enable/disable and voltage selection on representative buck/LDO supplies; run RTC read/set/alarm; and generate key/charger/audio IRQs where hardware supports them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/mt6358/registers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/mt6359/core.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/mt6359/core.h

## Purpose

This header defines MT6359 PMIC interrupt numbering and top-level IRQ grouping. It is the MT6359 counterpart to the MT6358 core IRQ header and is consumed by the shared `mt6358-irq` driver path.

## Important APIs, Types, and Functions

`enum mt6359_irq_top_status_shift` names top interrupt groups: BUCK, LDO, PSC, SCK, BM, HK, AUD at bit 7, and MISC. `enum mt6359_irq_numbers` assigns hardware IRQ numbers for buck over-current, LDO over-current, power/home key press and release, charger detect edge, RTC, fuel gauge, battery/thermal/AUXADC, audio/accessory, and SPI alert events. Base and bit-count macros derive group ranges, and `MT6359_TOP_GEN(sp)` constructs a `struct irq_top_t` initializer using MT6359 register constants.

## Control Flow

The header has no direct execution. The IRQ driver uses the generated top descriptors to walk from a top status bit to one or more group status registers and then to Linux nested IRQs. Enable and disable operations use the per-group enable register addresses and fixed register spacing encoded in the `MT6359_TOP_GEN()` macro.

## State and Persistence Behavior

Driver runtime state lives in `struct pmic_irq_data` from the MT6358 header, while hardware state lives in MT6359 registers. The enum values are persistent ABI inside the kernel tree because MFD cell resources and child drivers refer to them by number/name.

## Dependencies and Integration Points

This file relies on `struct irq_top_t`, `MTK_PMIC_REG_WIDTH`, and the MT6359 register map being included by the C file that uses it. It integrates with `drivers/mfd/mt6397-core.c` for child resources such as keys, RTC, and accessory detection, and with `drivers/mfd/mt6358-irq.c` for the actual IRQ domain setup.

## Risks and Edge Cases

The MT6359 top status layout differs from MT6358 because AUD starts at bit 7, leaving a gap. Treating top status bits as a dense sequence would route interrupts incorrectly. Several IRQ numbers are sparse by design; removing gaps changes register indexing. `MT6359_IRQ_BATON_BAT_OU` appears to be a truncated name but is part of the current exported enum spelling and should not be renamed casually without consumer updates.

## Test Signals

Compile `mt6358-irq.c` with MT6359 enabled, boot an MT6359 platform, verify `irq_create_mapping` for `MT6359_IRQ_RTC`, `MT6359_IRQ_PWRKEY`, and ACCDET resources, exercise PMIC key press/release, RTC alarm, charger detect edge, accessory detection, and at least one BM/HK interrupt path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/mt6359/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/mt6359/registers.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/mt6359/registers.h

## Purpose

This header provides the MT6359 PMIC register map and regulator bitfield contract used by MFD, IRQ, RTC, regulator, input, AUXADC, and sound consumers. Unlike the MT6358 register header, it includes many derived `RG_*`, `DA_*`, mask, and shift macros directly used by `mt6359-regulator.c`.

## Important APIs, Types, and Functions

The macro namespace includes chip and top interrupt addresses (`MT6359_SWCID`, `MT6359_TOP_INT_STATUS0`), RTC and secure RTC offsets, PSC/BM/HK/BUCK/LDO/AUD interrupt registers, buck control/debug/ELR addresses for VPU, VCORE, VGPU11, VMODEM, VPROC1/2, VS1/2, and VPA, LDO control/monitor blocks for RF, connectivity, camera, SIM, USB, VSRAM, VM18, VUFS and related rails, analog `*_ANA_CON0` addresses, and regulator helper macros such as `MT6359_RG_BUCK_VCORE_VOSEL_ADDR`, `MT6359_DA_VCORE_VOSEL_MASK`, `MT6359_RG_LDO_VSIM1_EN_SHIFT`, and `MT6359_RG_VBBCK_VOSEL_MASK`.

## Control Flow

No code runs in the header. Runtime flow is descriptor-driven: regulator registration builds descriptors from these address/mask/shift macros, regulator ops call regmap update/read helpers, IRQ setup uses top interrupt register addresses, and MFD core uses `MT6359_SWCID` plus IRQ constants from `mt6359/core.h` to instantiate child devices.

## State and Persistence Behavior

The mapped state is PMIC hardware state. Buck/LDO enable and voltage selections persist as PMIC register values until changed or reset; monitor `DA_*` addresses expose hardware-observed enable/voltage state; RTC registers hold time/alarm/power state; top interrupt registers latch and mask events. The header itself is stateless.

## Dependencies and Integration Points

Direct consumers include `drivers/regulator/mt6359-regulator.c`, `drivers/mfd/mt6358-irq.c`, `drivers/mfd/mt6397-core.c`, `drivers/input/keyboard/mtk-pmic-keys.c`, `drivers/iio/adc/mt6359-auxadc.c`, and MT6359 codec/accessory drivers. The register map also provides the base comparison point for `mt6359p/registers.h`, whose macros override shifted MT6359P addresses while reusing the same regulator driver.

## Risks and Edge Cases

Address, mask, and shift triples must remain synchronized; a correct address with an MT6359P shift, or a correct mask with the wrong monitor address, can produce silent voltage or status errors. Sparse register groups and multi-enable rails such as VCN33 and VUSB require descriptor care. Several `DA_*` monitor registers are read-only status paths, while `RG_*` registers are control paths; confusing them breaks set operations. Cross-including MT6359P macros in generic MT6359 code needs chip-version selection.

## Test Signals

Build and probe `mt6359-regulator`, verify every registered regulator can read status, test buck mode transitions and voltage changes, validate `TMA_KEY`-gated MT6359P paths are not used on plain MT6359, run RTC alarm and PMIC key IRQ tests, and use regmap debugfs traces to confirm descriptor operations hit expected `RG_*` and `DA_*` addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/mt6359/registers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/mt6359p/registers.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/mt6359p/registers.h

## Purpose

This header defines MT6359P-specific register addresses and helper macros for the MT6359 regulator driver. MT6359P is close enough to MT6359 to share driver logic, but many LDO monitor/control and ELR offsets differ; this file isolates those differences.

## Important APIs, Types, and Functions

The file exports `MT6359P_CHIP_VER`, key chip/version and trap/TMA-key addresses, MT6359P buck/LDO/analog register addresses, regulator helper address aliases such as `MT6359P_RG_BUCK_VCORE_VOSEL_ADDR`, `MT6359P_RG_LDO_VSRAM_PROC1_VOSEL_ADDR`, `MT6359P_RG_LDO_VUSB_EN_0_ADDR`, and `MT6359P_RG_VBBCK_VOSEL_ADDR`, plus `MT6359P_VM_MODE_ADDR`, `MT6359P_TMA_KEY_ADDR`, and `TMA_KEY`.

## Control Flow

The header itself has no flow. `mt6359-regulator.c` selects MT6359P descriptors for MT6359P hardware and then uses these macros in normal regulator operations. For some VM mode reads, the driver writes `TMA_KEY` to `MT6359P_TMA_KEY_ADDR`, reads `MT6359P_VM_MODE_ADDR`, and clears the key afterward.

## State and Persistence Behavior

No memory is owned here. The macros target persistent PMIC control state for regulators and protected test/mode access. The TMA key sequence is transient but security-sensitive: leaving the key enabled or writing it on the wrong chip can expose or alter protected PMIC state.

## Dependencies and Integration Points

The header is included by `drivers/regulator/mt6359-regulator.c` alongside `mt6359/registers.h` and `mt6397/core.h`. It assumes the shared MT6359 regulator IDs and descriptor machinery, while providing MT6359P-specific address overrides and the chip-version constant used for hardware selection.

## Risks and Edge Cases

MT6359P offsets often differ by small increments from MT6359 offsets, making copy/paste mistakes hard to spot. Some macros intentionally map VA09 and VA12 voltage selection to ELR registers rather than the apparent analog control addresses. TMA-key writes must be paired with cleanup even on errors. Because many helper macros omit masks/shifts and rely on MT6359 defaults, descriptor code must ensure reused defaults are valid for MT6359P.

## Test Signals

Probe on MT6359P hardware and verify chip version `0x5930`; register all expected regulators; exercise VCORE, VGPU11 SSHUB, VSRAM, VEMC, VUSB, VA09, and VA12 voltage reads/sets; run error-path tests or fault injection around TMA key read sequences; and confirm plain MT6359 hardware still uses the non-P addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/mt6359p/registers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/mt6397/core.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/mt6397/core.h

## Purpose

This header defines the common core data structure and chip ID/IRQ contracts for the MediaTek MT6397-family PMIC MFD driver. It is shared by the parent MFD core, IRQ implementations, and child drivers that need the parent regmap or chip identity.

## Important APIs, Types, and Functions

`enum chip_id` lists supported PMIC IDs: MT6323, MT6328, MT6331, MT6332, MT6357, MT6358, MT6359, MT6366, MT6391, and MT6397. `enum mt6397_irq_numbers` defines legacy MT6397 IRQ hwirqs for speaker, battery, watchdog, keys, charger, over-voltage, LDO, audio, RTC, HDMI, and regulator events. `struct mt6397_chip` is the central parent object with `dev`, `regmap`, notifier block, parent IRQ, irqdomain, `irqlock`, wake/current/cache mask arrays, interrupt control/status register arrays, `chip_id`, and opaque `irq_data`. The exported prototypes are `mt6358_irq_init()` and `mt6397_irq_init()`.

## Control Flow

The MFD probe allocates and fills `struct mt6397_chip`, reads chip ID using a chip-specific address, calls the selected IRQ initializer, and then registers child `mfd_cell`s. Child drivers call `dev_get_drvdata(pdev->dev.parent)` to recover this structure and use the shared regmap. IRQ init functions populate irqdomain and mask state before child resources are mapped.

## State and Persistence Behavior

`struct mt6397_chip` holds runtime kernel state for IRQ masking, wake masks, cached masks, and chip metadata. It does not persist across reboot. The regmap points to PMIC hardware registers whose state may persist across AP resets depending on PMIC power domains. The notifier block supports power-management integration for wake/mask handling.

## Dependencies and Integration Points

The header includes mutex and notifier declarations and relies on forward declarations from included Linux headers for devices, regmap, and irqdomain in consumers. It integrates with `drivers/mfd/mt6397-core.c`, `mt6397-irq.c`, `mt6358-irq.c`, regulator drivers, `rtc-mt6397.c`, PMIC key drivers, pinctrl, LED, poweroff, AUXADC, and MediaTek codec drivers.

## Risks and Edge Cases

The fixed-size IRQ arrays of length 3 match legacy MT6397 interrupt register layout; newer chips use `irq_data` for richer topology, so code must not assume every chip uses only the arrays. `chip_id` is a 16-bit field while `enum chip_id` values are short IDs; callers must compare the same representation. Locking around mask caches is critical because parent IRQ handling and child enable/disable paths can race.

## Test Signals

Build all MT6397-family MFD variants, boot on at least one legacy MT6397 and one MT6358/MT6359-family board, verify child devices probe from the parent, inspect irqdomain mappings, exercise suspend/resume wake masks, and run regulator, RTC, key, and pinctrl smoke tests using the shared parent regmap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/mt6397/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/mt6397/registers.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/mt6397/registers.h

## Purpose

This header is the legacy MT6397 PMIC register map. It covers top-level clock/reset/status, interrupt control/status, EFUSE, buck regulators, LDO regulators, speaker, audio DAC/buffer/ADC, zero-cross detection, and related analog/audio blocks.

## Important APIs, Types, and Functions

The exported API is the `MT6397_*` register macro namespace. Key definitions include `MT6397_CID`, `MT6397_TOP_CKPDN*`, `MT6397_TOP_RST_*`, `MT6397_INT_CON0`, `MT6397_INT_CON1`, `MT6397_INT_STATUS0`, `MT6397_INT_STATUS1`, EFUSE data registers, buck register blocks such as `MT6397_VCA15_CON*`, `MT6397_VCORE_CON*`, and `MT6397_VGPU_CON*`, LDO blocks such as `MT6397_ANALDO_CON*` and `MT6397_DIGLDO_CON*`, speaker registers, and audio registers such as `MT6397_AUDDAC_CON0`, `MT6397_AUDADC_CON*`, and `MT6397_ZCD_CON*`.

## Control Flow

No executable flow is defined. `mt6397-core.c` reads chip ID and instantiates children with resources. `mt6397-irq.c` uses interrupt control/status registers for the legacy IRQ controller. `mt6397-regulator.c` maps regulator descriptors to buck/LDO addresses and selects voltage registers at probe time. PMIC key and audio consumers use the same address contract for event and codec handling.

## State and Persistence Behavior

The header maps PMIC hardware state. Interrupt masks/latches, EFUSE values, regulator voltages/enables, audio analog settings, and clock/reset controls are hardware state; some are volatile, while EFUSE and certain retention/power-domain registers are persistent or reset-domain-dependent. The header itself stores nothing.

## Dependencies and Integration Points

It is paired with `mt6397/core.h` and consumed by MFD, IRQ, regulator, key, pinctrl, LED, RTC resource, and codec paths. Macro names are embedded in regulator descriptor tables, so address names and chip revision quirks must stay aligned with `drivers/regulator/mt6397-regulator.c`.

## Risks and Edge Cases

MT6397 uses a different RTC base/resource style than MT6357/6358/6359, so mixing register maps across chips is unsafe. Regulator descriptors rely on control register offsets and bit positions outside this file; address drift creates hard-to-diagnose voltage behavior. Interrupt status/control registers are only two primary groups for this legacy chip, unlike newer top-group PMIC IRQ maps.

## Test Signals

Build and boot MT6397 MFD and regulator drivers; read `MT6397_CID`; verify regulator registration and voltage control for buck and LDO rails; exercise PMIC key and RTC resources; check IRQ mask/status behavior with `/proc/interrupts`; and validate audio codec paths when MT6397 audio is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/mt6397/registers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/mt6397/rtc.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/mt6397/rtc.h

## Purpose

This header defines the common RTC register offsets, bit masks, timing constants, chip data, and runtime state structure for MediaTek PMIC RTC drivers in the MT6397 family.

## Important APIs, Types, and Functions

Important register and bit macros include `RTC_BBPU`, `RTC_BBPU_CBUSY`, `RTC_BBPU_KEY`, chip-specific write-trigger registers `RTC_WRTGR_MT6358`, `RTC_WRTGR_MT6397`, and `RTC_WRTGR_MT6323`, IRQ bits `RTC_IRQ_STA_AL`, `RTC_IRQ_STA_LP`, `RTC_IRQ_EN_AL`, `RTC_IRQ_EN_ONESHOT`, `RTC_IRQ_EN_LP`, alarm masks, time counter offsets from `RTC_TC_SEC`, alarm field masks, `RTC_PDN2_PWRON_ALARM`, and poll timing constants. `struct mtk_rtc_data` carries the write-trigger offset. `struct mt6397_rtc` stores the registered RTC device, lock, regmap, IRQ, address base, and chip data.

## Control Flow

The RTC driver uses `addr_base` plus these offsets to read time registers, set alarm registers, enable or clear IRQs, and trigger writes through the chip-specific `wrtgr` register. Busy polling uses `RTC_BBPU_CBUSY` with `MTK_RTC_POLL_DELAY_US` and `MTK_RTC_POLL_TIMEOUT`. The driver lock serializes register sequences because time/alarm updates require multiple register writes plus a final trigger.

## State and Persistence Behavior

`struct mt6397_rtc` is runtime kernel state. The RTC hardware maintains persistent time, alarm, PDN, and power-on-alarm bits in the PMIC RTC domain. `RTC_PDN2_PWRON_ALARM` can influence boot/power behavior. The write-trigger register is a commit mechanism: values staged into time/alarm registers are not fully applied until the trigger sequence completes.

## Dependencies and Integration Points

The header includes jiffies, mutex, regmap, and RTC core headers. It is included by `drivers/rtc/rtc-mt6397.c` and by `drivers/power/reset/mt6323-poweroff.c` for RTC poweroff/power-on behavior. The parent MFD provides the regmap, IRQ resource, and chip-specific RTC base.

## Risks and Edge Cases

Month/year masks are hardware-specific and narrow, so date conversion must handle century offsets correctly in the C driver. Multi-register time reads can race rollover unless the driver uses stable read patterns. Failure to poll `CBUSY` or to trigger writes leaves stale hardware state. Incorrect `wrtgr` selection breaks only some chips, making cross-chip tests important.

## Test Signals

Use RTC class tests for read/set, alarm set/enable/interrupt, and wake from suspend; test boundary dates and month rollover; check busy-poll timeout behavior with fault injection if possible; verify MT6358/MT6397/MT6323 write-trigger variants; and confirm power-on-alarm behavior through reboot or power-cycle tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/mt6397/rtc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/mxs-lradc.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/mxs-lradc.h

## Purpose

This header defines the shared Freescale/NXP MXS low-resolution ADC register contract and parent state used by IIO, touchscreen, and touch-button child drivers. It covers i.MX23 and i.MX28 differences.

## Important APIs, Types, and Functions

The macro API includes channel limits, delay timer rate, control/status/channel/delay register offsets, touch plate switch bits for MX23 and MX28, IRQ enable/status masks, ADC channel sample/value fields, delay trigger/loop/kick helpers, LRADC channel selection helpers, resolution and sample masks, buffer virtual-channel masks, and reserved channel masks for touchbutton and 4/5-wire touchscreen use. `enum mxs_lradc_id` identifies IMX23 vs IMX28. `enum mxs_lradc_ts_wires` identifies touchscreen wiring. `struct mxs_lradc` stores SoC type, delay clock, available buffered channels, touchscreen mode, and touchbutton usage. `mxs_lradc_irq_mask()` returns the SoC-specific IRQ bit mask.

## Control Flow

There is only one inline control path: `mxs_lradc_irq_mask()` switches on `lradc->soc` and returns the correct IRQ mask. Runtime child drivers use the macros to program touch detection, map virtual channels, configure sample accumulation, set delay triggers, clear IRQs, and read raw channel values.

## State and Persistence Behavior

`struct mxs_lradc` is runtime parent state shared by MFD children. The hardware state consists of ADC control registers, virtual channel mappings, delay timers, pending IRQs, and touch plate switch configuration. No file-backed persistence is involved. Channel availability is stateful at runtime because touchscreen or touchbutton use reserves channels from generic buffered sampling.

## Dependencies and Integration Points

The header includes bit operations, MMIO helpers, and STMP register helper declarations. It is consumed by LRADC MFD core code, IIO ADC support, and `drivers/input/touchscreen/mxs-lradc-ts.c`, whose touch state machine uses the plate masks, delay registers, channel mappings, and `mxs_lradc_irq_mask()`.

## Risks and Edge Cases

MX23 and MX28 bit layouts differ; using the wrong plate or IRQ mask can short or misdrive touchscreen lines. Shared channel masks are important because generic ADC sampling must not use channels currently reserved for touch hardware. Delay fields are limited-width, so unmasked values would corrupt adjacent trigger bits. The default branch in `mxs_lradc_irq_mask()` returns zero, which makes an unknown SoC fail quietly by ignoring IRQs.

## Test Signals

Build MXS LRADC MFD/IIO/touchscreen drivers for IMX23 and IMX28; probe with device tree touchscreen and touchbutton modes; verify generic ADC channels reject reserved touch channels; exercise touch IRQs and coordinate/pressure reads; test delay-triggered sampling; and inspect register writes on both SoC variants if hardware tracing is available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/mxs-lradc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/nct6694.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/nct6694.h

## Purpose

This header defines the shared USB transaction ABI, IRQ IDs, and parent state for the Nuvoton NCT6694 USB MFD device. It is the contract between the core USB MFD driver and child GPIO, I2C, CAN-FD, RTC, watchdog, and hwmon drivers.

## Important APIs, Types, and Functions

Constants define USB identity and endpoints (`NCT6694_VENDOR_ID`, `NCT6694_PRODUCT_ID`, interrupt/bulk endpoints), host control direction bits, and `NCT6694_URB_TIMEOUT`. `enum nct6694_irq_id` assigns IRQ domain hwirqs for GPIO groups 0-F, CAN0/1, and RTC. `enum nct6694_response_err_status` names device response statuses. Packed `struct nct6694_cmd_header`, `struct nct6694_response_header`, and `union nct6694_usb_msg` define the on-wire message header format. `struct nct6694` stores parent device state: ID allocators for child instances, irqdomain, locks, interrupt URB, USB device, shared message buffer, interrupt buffer, and enabled IRQ bitmap. The exported functions are `nct6694_read_msg()` and `nct6694_write_msg()`.

## Control Flow

Child drivers build a `nct6694_cmd_header` with module, offset or command/selector, transfer direction, and payload length, then call `nct6694_read_msg()` or `nct6694_write_msg()`. The core serializes USB access with `access_lock`, submits bulk transfers, interprets `nct6694_response_header`, and maps interrupt bits from the interrupt endpoint through the irqdomain to child IRQ handlers.

## State and Persistence Behavior

`struct nct6694` is runtime kernel state. Device configuration changed through child write messages persists according to the NCT6694 firmware/hardware behavior, not this header. `irq_enable` tracks enabled IRQ bits in memory, while the device sends interrupt reports through `int_in_urb` and `int_buffer`.

## Dependencies and Integration Points

Consumers include `drivers/mfd/nct6694.c`, `gpio-nct6694.c`, `i2c-nct6694.c`, `nct6694_canfd.c`, `rtc-nct6694.c`, `nct6694_wdt.c`, and `nct6694-hwmon.c`. The packed header layout is an ABI with device firmware, so endian annotations and field order are integration-critical.

## Risks and Edge Cases

Packed USB structures must match firmware exactly; padding or endian mistakes corrupt every child protocol. `len` must match the child payload union size or transfers can truncate/overrun. Response statuses such as timeout, pending, and no response need consistent error mapping. Shared `usb_msg` and buffers require serialization; concurrent child transactions without `access_lock` would race. IRQ IDs are finite and an incorrect offset can route GPIO/CAN/RTC events to the wrong child.

## Test Signals

Compile all NCT6694 child drivers, probe a USB device with VID `0x0416` and PID `0x200B`, run read/write transactions for each module, test response error handling with unplug/timeout scenarios, verify GPIO IRQ mapping for multiple groups, exercise CAN-FD, RTC alarm, watchdog ping/start/stop, and hwmon read/write paths, and enable USB tracing to confirm header lengths and endpoints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/nct6694.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/ntxec.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/ntxec.h

## Purpose

This header defines the shared parent object and register-value helper for the Netronix embedded controller used in e-reader platforms. It also records known firmware version constants.

## Important APIs, Types, and Functions

`struct ntxec` stores the parent `device` and `regmap` used by child drivers. `ntxec_reg8(u8 value)` converts an 8-bit register payload into the big-endian 16-bit representation expected by EC registers that carry the meaningful byte in the first transmitted byte. Firmware constants identify Kobo Aura, Tolino Shine 2 HD, and Tolino Vision variants.

## Control Flow

The only executable flow is the inline `ntxec_reg8()` left-shift. Runtime child drivers retrieve `struct ntxec` from their parent, then perform regmap reads/writes. For example, `rtc-ntxec.c` writes time fields by wrapping 8-bit values with `ntxec_reg8()` before writing the EC's 16-bit register protocol.

## State and Persistence Behavior

The header owns no storage. `struct ntxec` is runtime parent state around an I2C-backed regmap. EC registers hold device state such as RTC, battery, ADC, PWM, or home-pad data depending on firmware. Some values, especially RTC state, persist in the embedded controller across host sleep or reboot.

## Dependencies and Integration Points

It includes Linux integer types and forward-declares `struct device` and `struct regmap`, keeping the header lightweight. Child drivers such as `drivers/rtc/rtc-ntxec.c` include it for parent access and endian conversion. Firmware version constants are integration signals for feature gating and board-specific behavior.

## Risks and Edge Cases

The EC has mixed register semantics: some registers are true big-endian 16-bit values, while others are 8-bit values in the MSB position. Using `ntxec_reg8()` on a real 16-bit value or forgetting it on an 8-bit register causes byte-swapped behavior. Firmware variants expose different feature sets, so assuming all versions have RTC/ADC/PWM/home-pad support is unsafe.

## Test Signals

Build Netronix EC child drivers, probe known firmware versions, verify regmap byte order with a harmless 8-bit register, run RTC read/set on `rtc-ntxec`, test feature gating against firmware constants, and use I2C tracing to confirm 8-bit writes are shifted into the first transmitted byte.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/ntxec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/ocelot.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/ocelot.h

## Purpose

This header provides helper functions for obtaining regmaps from Ocelot/VSC7512-style platform resources in both standalone MMIO and MFD-child configurations.

## Important APIs, Types, and Functions

`ocelot_regmap_from_resource_optional()` attempts to map an `IORESOURCE_MEM` resource at a given index with `devm_ioremap_resource()` and create a MMIO regmap with `devm_regmap_init_mmio()`. If no memory resource exists and the platform device has a parent, it falls back to an `IORESOURCE_REG` resource and returns a named regmap from the parent with `dev_get_regmap()`. Missing optional resources return `NULL`; mapping errors return `ERR_PTR`. `ocelot_regmap_from_resource()` wraps the optional helper and converts a missing resource to `ERR_PTR(-ENOENT)`.

## Control Flow

The control path is a two-stage lookup: first direct MMIO resource, then MFD parent regmap by named register resource. The non-optional wrapper preserves errors and converts `NULL` to a standard missing-resource error. Consumers call this during probe before registering pinctrl, SGPIO, or MDIO functionality.

## State and Persistence Behavior

The functions allocate devm-managed mappings/regmaps when direct MMIO is present. Parent-regmap fallback returns an existing parent-owned regmap and does not create new persistent state. Hardware state is the target register region; this header only standardizes how child drivers acquire access.

## Dependencies and Integration Points

The header includes platform device, resource, regmap, error, and type helpers. Direct users include `drivers/pinctrl/pinctrl-microchip-sgpio.c`, `drivers/pinctrl/pinctrl-ocelot.c`, and `drivers/net/mdio/mdio-mscc-miim.c`. It integrates standalone platform devices with MFD cells that expose `IORESOURCE_REG` names matching parent regmaps.

## Risks and Edge Cases

The optional helper intentionally avoids noisy resource lookup for absent optional MMIO resources; callers must distinguish `NULL` from an error pointer. In MFD mode, resource names must match parent regmap names exactly. If a device has neither direct memory nor parent regmap resources, the required wrapper returns `-ENOENT`. Passing the wrong `regmap_config` for a direct mapping can produce invalid register stride/width behavior.

## Test Signals

Build Ocelot pinctrl, SGPIO, and MSCC MIIM consumers; probe both standalone MMIO and MFD child device-tree descriptions; verify optional second MDIO regmap absence returns `NULL` without probe failure where expected; validate required resources fail with `-ENOENT`; and use regmap debugfs to confirm operations target direct or parent-backed maps as intended.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/ocelot.h -->
