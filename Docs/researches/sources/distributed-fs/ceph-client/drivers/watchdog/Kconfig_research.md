# sources/distributed-fs/ceph-client/drivers/watchdog/Kconfig

## Purpose

`sources/distributed-fs/ceph-client/drivers/watchdog/Kconfig` is the configuration registry for Linux watchdog support. It defines the top-level `WATCHDOG` menu, core framework and policy options, pretimeout governors, and a large catalog of hardware/software watchdog driver symbols grouped by architecture or bus type. The complete 2357-line file was read for this report.

## Important APIs, Types, and Functions

This is Kconfig data rather than C code. Key symbols include `WATCHDOG`, `WATCHDOG_CORE`, `WATCHDOG_NOWAYOUT`, `WATCHDOG_HANDLE_BOOT_ENABLED`, `WATCHDOG_OPEN_TIMEOUT`, `WATCHDOG_SYSFS`, `WATCHDOG_HRTIMER_PRETIMEOUT`, `WATCHDOG_PRETIMEOUT_GOV`, `WATCHDOG_PRETIMEOUT_GOV_NOOP`, and `WATCHDOG_PRETIMEOUT_GOV_PANIC`. Driver symbols relevant to this work item include `ACQUIRE_WDT`, `ADVANTECH_WDT`, `ADVANTECH_EC_WDT`, `AIROHA_WATCHDOG`, `ALIM1535_WDT`, `ALIM7101_WDT`, `APPLE_WATCHDOG`, `ARM_SMC_WATCHDOG`, `ARMADA_37XX_WATCHDOG`, `ASM9260_WATCHDOG`, `ASPEED_WATCHDOG`, `AT91RM9200_WATCHDOG`, `AT91SAM9X_WATCHDOG`, `ATH79_WDT`, `BCM2835_WDT`, `BCM47XX_WDT`, `BCM7038_WDT`, and `BCM_KONA_WDT`. The file also declares dependencies such as `HAS_IOPORT`, `PCI`, `OF`, `HAS_IOMEM`, architecture symbols, `COMPILE_TEST`, and selects such as `WATCHDOG_CORE`, `MFD_SYSCON`, `ISA_BUS_API`, `RESET_CONTROLLER`, or `REGMAP`.

## Control Flow

Kconfig evaluation flows from `menuconfig WATCHDOG`; all subordinate options are only visible inside `if WATCHDOG`. Core options and pretimeout choices come first, followed by architecture-independent drivers, ARM, x86, MIPS, PowerPC, and other architecture groups, then ISA/PCI/USB card drivers. `choice` selects the default pretimeout governor when governor support is enabled. Driver `depends on`, `select`, and `default` lines determine whether the corresponding object can be built and whether helper subsystems are pulled in.

## State and Persistence Behavior

The file contributes build-time state to `.config`. Some options also influence runtime behavior through defaults used by drivers or the watchdog core, especially `WATCHDOG_NOWAYOUT`, `WATCHDOG_HANDLE_BOOT_ENABLED`, and `WATCHDOG_OPEN_TIMEOUT`. No runtime storage is owned here.

## Dependencies and Integration Points

The main integration is with `drivers/watchdog/Makefile`, which maps each `CONFIG_*` symbol to an object file. It also integrates with driver source assumptions: symbols that do not select `WATCHDOG_CORE` generally provide their own legacy miscdevice interface, while modern watchdog-core drivers select `WATCHDOG_CORE`. Architecture and bus dependencies prevent drivers from appearing where required register access, platform discovery, or firmware interfaces are absent.

## Risks and Edge Cases

Over-broad `COMPILE_TEST` paths can expose missing includes or unguarded architecture assumptions. Missing `select WATCHDOG_CORE` for a core-based driver would cause link failures; selecting too much can force unintended dependencies. Legacy drivers that do not use `WATCHDOG_CORE` still share `/dev/watchdog` semantics and may conflict with core drivers at runtime. Dependency changes affect whether users can build critical reset paths such as Apple or Aspeed watchdogs.

## Test Signals

Run Kconfig and allmodconfig/allnoconfig/allyesconfig build coverage across representative architectures; verify each enabled symbol builds the object listed in `Makefile`; check `COMPILE_TEST` combinations; and validate visible prompts/help text for new or changed watchdog entries.
