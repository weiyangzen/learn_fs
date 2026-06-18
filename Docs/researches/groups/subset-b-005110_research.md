# subset-b-005110 Research

Grouped source-tree-aligned research for Linux pinctrl drivers under Sophgo, Spacemit, and SPEAr. Each section is delimited for reconciliation into the mapped per-file report path.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sophgo/pinctrl-cv1812h.c -->
## `sources/distributed-fs/ceph-client/drivers/pinctrl/sophgo/pinctrl-cv1812h.c`

Purpose: SoC-specific Sophgo CV1812H pinctrl data and electrical characteristics. The file supplies a generated pin descriptor table, per-pin register metadata, power-domain names, VDDIO conversion helpers, and the platform driver binding for `sophgo,cv1812h-pinctrl`. It does not implement generic pinctrl algorithms itself; it binds CV1812H data to the shared CV18xx/Sophgo helpers.

Important APIs/types/functions: `cv1812h_get_pull_up()`, `cv1812h_get_pull_down()`, `cv1812h_get_oc_map()`, and `cv1812h_get_schmitt_map()` implement `struct sophgo_vddio_cfg_ops`. `cv1812h_pins[]` exposes `PINCTRL_PIN()` descriptors from `dt-bindings/pinctrl/pinctrl-cv1812h.h`. `cv1812h_pin_data[]` uses `CV1800_GENERAL_PIN`, `CV1800_FUNC_PIN`, and `CV1800_GENERATE_PIN_MUX2` to map each pin to a power domain, IO type, mux register, optional second mux register, and pinconf register. `cv1812h_pindata` links these tables to `cv1800_cfg_ops`, `cv1800_pctrl_ops`, `cv1800_pmx_ops`, and `cv1800_pconf_ops`.

Control flow: matching `sophgo,cv1812h-pinctrl` feeds `cv1812h_pindata` into `sophgo_pinctrl_probe()`. The shared probe maps resources, registers pinctrl ops, and later DT child nodes are parsed by the common CV18xx path. Pinconf get/set paths call back into this file to translate pull, drive-strength, and Schmitt values for each IO type and voltage.

State and persistence: the file itself contains immutable tables. Runtime voltage state is stored by the shared CV18xx private `power_cfg[]`, and this file's conversion callbacks read that state through the supplied `psmap`. No persistent storage is used beyond MMIO register effects applied by common code.

Dependencies and integration: depends on CV18xx shared header/ops, Linux module/platform/of/pinctrl APIs, and CV1812H DT binding constants. It integrates with board DT via compatible string and `pinmux` encodings whose pin IDs must match the binding table. Risks are mostly data-quality risks: generated offset mistakes, incorrect power-domain assignment, and wrong electrical maps can produce silent misconfiguration. Test signals include successful probe with `sys`/`rtc` resources, pinctrl debug output showing expected power domains/registers, DT groups using valid `power-source`, and exercising pull/drive/schmitt settings on both 1.8V-only and 1.8V-or-3.3V domains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sophgo/pinctrl-cv1812h.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sophgo/pinctrl-cv18xx.c -->
## `sources/distributed-fs/ceph-client/drivers/pinctrl/sophgo/pinctrl-cv18xx.c`

Purpose: shared pinctrl/pinmux/pinconf implementation for Sophgo CV18xx-style SoCs. It handles DT pinmux decoding, validation, group/function registration, mux writes, pinconf conversion, pinconf reads, and MMIO setup for two register areas named `sys` and `rtc`.

Important APIs/types/functions: `struct cv1800_priv` stores `power_cfg[]` and `regs[2]`. `cv1800_dt_get_pin_mux()` and `cv1800_dt_get_pin_mux2()` decode mux fields from a 32-bit DT pinmux value. `cv1800_verify_pinmux_config()` bounds mux values and enforces mux2 rules; `cv1800_verify_pin_group()` requires multi-pin groups to share IO type and power domain. `cv1800_dt_node_to_map_post()` requires a `power-source` property and records one voltage per power domain. Exported ops are `cv1800_pctrl_ops`, `cv1800_pmx_ops`, `cv1800_pconf_ops`, and `cv1800_cfg_ops`.

Control flow: `sophgo_pinctrl_probe()` invokes `cv1800_pinctrl_init()`, which allocates private state and maps `sys`/`rtc` resources. DT parsing flows through the Sophgo common `sophgo_pctrl_dt_node_to_map()`, which calls this file's validation and post-parse hooks. Mux selection calls `sophgo_pmx_set_mux()`, which invokes `cv1800_set_pinmux_config()` for each pin. Pinconf set calls `cv1800_pinconf_compute_config()` to produce value/mask bits, then `cv1800_set_pinconf_config()` performs read-modify-write. Pinconf get reads a pin's conf register and converts fields back to generic pinconf arguments.

State and persistence: `power_cfg[]` records selected per-domain voltage for the lifetime of the driver. A domain can be set once, or set again to the same voltage; conflicting later groups return `-EINVAL`. Hardware state lives in pin mux/conf registers and persists until reset or overwritten.

Dependencies and integration: relies on `pinctrl-sophgo-common.c` for generic registration/parsing, SoC-specific data in CV1812H/SG200x files, `dt-bindings/pinctrl/pinctrl-cv18xx.h`, Linux generic pinconf helpers, and MMIO resource names. Risks include required `power-source` rejecting legacy DT, missing NULL checks in debug paths if invalid pin IDs reach callbacks, and group-wide pinconf using the first pin's electrical conversion for every pin. Test signals include invalid mux rejection, mux2 validation, repeated same-voltage group acceptance, cross-voltage conflict rejection, and pinconf round-trips for pull, drive strength in microamps, Schmitt threshold, slew rate, and bus hold.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sophgo/pinctrl-cv18xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sophgo/pinctrl-cv18xx.h -->
## `sources/distributed-fs/ceph-client/drivers/pinctrl/sophgo/pinctrl-cv18xx.h`

Purpose: shared type and macro contract for Sophgo CV18xx-family pinctrl drivers. It defines the pin data layout consumed by the common CV18xx implementation and used by generated SoC pin tables.

Important APIs/types/functions: `enum cv1800_pin_io_type` distinguishes 1.8V-only, 1.8V-or-3.3V, audio, and Ethernet pins. `CV1800_PINCONF_AREA_SYS` and `CV1800_PINCONF_AREA_RTC` identify register banks. `struct cv1800_pinmux`, `struct cv1800_pinmux2`, and `struct cv1800_pinconf` carry register offset, area, mux limits, and mux2 parent function information. `struct cv1800_pin` embeds `struct sophgo_pin` plus power domain and register descriptors. `cv1800_pin_io_type()` decodes flags. Macros `CV1800_FUNC_PIN`, `CV1800_GENERAL_PIN`, and `CV1800_GENERATE_PIN_MUX2` are the table-authoring interface used by CV1812H, SG2000, and SG2002.

Control flow: this header has no runtime control flow, but it determines how the shared ops interpret SoC table entries. The `CV1800_PIN_HAVE_MUX2` flag causes validation and mux writes to use a secondary mux register; `CV1800_PIN_IO_TYPE` drives which pinconf operations are supported and which VDDIO conversion maps are chosen.

State and persistence: no runtime state is stored here. The struct layout is part of the persistent compile-time ABI between SoC tables and shared ops; `pinsize` in `struct sophgo_pinctrl_data` must match `sizeof(struct cv1800_pin)` so `bsearch()` can traverse the data safely.

Dependencies and integration: includes Linux bitfield and pinctrl headers plus `pinctrl-sophgo.h`. It exposes `cv1800_pctrl_ops`, `cv1800_pmx_ops`, `cv1800_pconf_ops`, and `cv1800_cfg_ops` for SoC files. Risks include macro misuse, unsorted pin arrays breaking shared `bsearch()`, mismatched mux limits, and stale DT binding IDs. Test signals are build-time coverage of all macro users, probe-time pin lookup success for each binding ID, and DT cases that exercise mux2 and audio/Ethernet unsupported pinconf paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sophgo/pinctrl-cv18xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sophgo/pinctrl-sg2000.c -->
## `sources/distributed-fs/ceph-client/drivers/pinctrl/sophgo/pinctrl-sg2000.c`

Purpose: SoC-specific pin table and electrical map provider for Sophgo SG2000 pinctrl. It is structurally aligned with CV1812H, using the shared CV18xx implementation and generated vendor pinout definitions under `dt-bindings/pinctrl/pinctrl-sg2000.h`.

Important APIs/types/functions: `sg2000_get_pull_up()`, `sg2000_get_pull_down()`, `sg2000_get_oc_map()`, and `sg2000_get_schmitt_map()` implement VDDIO conversions. The `SG2000_POWER_DOMAIN` enum and `sg2000_power_domain_desc[]` name eight domains including EPHY, MIPI, eMMC, RTC, SD0, SD1, and VIVO. `sg2000_pins[]` lists all visible pinctrl pins, and `sg2000_pin_data[]` maps them to CV18xx mux/conf register descriptors. `sg2000_pindata` connects the SoC data to `cv1800_*` ops.

Control flow: `module_platform_driver()` registers `sg2000_pinctrl_driver`; `sophgo_pinctrl_probe()` receives `sg2000_pindata` from the OF match. Runtime parsing, mux setting, and pinconf handling are delegated to `pinctrl-cv18xx.c`, which calls SG2000 VDDIO callbacks when converting generic pinconf arguments.

State and persistence: compile-time tables are immutable. Runtime state is shared CV18xx state: per-power-domain voltage choices are stored once in `power_cfg[]`, and register writes persist in the SoC pinmux/pinconf MMIO blocks.

Dependencies and integration: depends on the CV18xx header and common Sophgo backend, Linux module/platform/of/pinctrl APIs, and SG2000 binding constants. The table includes pins with `IO_TYPE_AUDIO` and `IO_TYPE_ETH`, which mux normally but reject generic CV18xx pinconf. Risks include generated-table drift, wrong domain voltage maps, cross-domain grouping rejected by common validation, and inconsistent binding IDs. Test signals include DT compatible match `sophgo,sg2000-pinctrl`, successful mux on representative camera/MIPI/SD/eMMC/RTC pins, rejected invalid mux2 encodings, voltage conflict tests, and pinconf conversion tests over both 1.8V and 3.3V domains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sophgo/pinctrl-sg2000.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sophgo/pinctrl-sg2002.c -->
## `sources/distributed-fs/ceph-client/drivers/pinctrl/sophgo/pinctrl-sg2002.c`

Purpose: SG2002-specific CV18xx-family pinctrl data provider. It supplies a smaller/reshaped pin table and condensed power-domain model while reusing the same shared CV18xx ops and electrical conversion style as CV1812H/SG2000.

Important APIs/types/functions: `SG2002_POWER_DOMAIN` defines five domains: MIPI, USB/PLL/ETH, RTC, SD0/eMMC, and SD1. `sg2002_get_pull_up()`, `sg2002_get_pull_down()`, `sg2002_get_oc_map()`, and `sg2002_get_schmitt_map()` provide VDDIO maps for 1.8V-only, 1.8V/3.3V, and Ethernet IO types. `sg2002_pins[]` lists pins in binding order, while `sg2002_pin_data[]` maps each to mux/conf offsets across `sys` and `rtc`. `sg2002_pindata` plugs those arrays into `cv1800_cfg_ops`, `cv1800_pctrl_ops`, `cv1800_pmx_ops`, and `cv1800_pconf_ops`.

Control flow: OF compatible `sophgo,sg2002-pinctrl` selects `sg2002_pindata`; the common Sophgo probe and CV18xx callbacks do all parsing and register programming. The SoC callbacks are used only when generic pinconf needs typical pull resistance, output-current map, or Schmitt threshold conversion.

State and persistence: this file has static immutable tables. The shared runtime keeps per-domain voltage selections in `power_cfg[]`; because SG2002 merges several rails into broad domains, a board DT conflict in one functional area can affect other pins in the same logical domain. MMIO writes made by common ops persist until overwritten or reset.

Dependencies and integration: depends on SG2002 DT binding IDs, the CV18xx shared header, and Linux pinctrl/platform infrastructure. Risks include condensed domain modeling rejecting mixed-voltage configurations, generated offset mistakes, unsupported audio pinconf, and power-source omission causing DT map failures. Test signals include probe on `sophgo,sg2002-pinctrl`, group validation for SD0/eMMC sharing, mux2 tests for MIPI RX pins, Ethernet drive-strength reads, and negative tests for invalid `power-source` or mux values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sophgo/pinctrl-sg2002.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sophgo/pinctrl-sg2042-ops.c -->
## `sources/distributed-fs/ceph-client/drivers/pinctrl/sophgo/pinctrl-sg2042-ops.c`

Purpose: shared SG2042/SG2044 pinctrl operations. Unlike CV18xx, these SoCs use one MMIO region and pack a pin's configuration into a 16-bit slot, sometimes in the high halfword of a 32-bit register. This file implements generic pinctrl, mux, pinconf, and probe-time MMIO setup for tables described by `struct sg2042_pin`.

Important APIs/types/functions: `struct sg2042_priv` stores the mapped register base. `sg2042_get_pin_reg()` and `sg2042_set_pin_reg()` read/write the low or high 16-bit slot according to `PIN_FLAG_WRITE_HIGH`. `sg2042_set_pinmux_config()` writes `PIN_IO_MUX` unless `PIN_FLAG_NO_PINMUX` is set. `sg2042_pconf_get()` and `sg2042_pinconf_compute_config()` handle bias disable/up/down, drive strength in microamps, and input Schmitt enable. Exported ops are `sg2042_pctrl_ops`, `sg2042_pmx_ops`, `sg2042_pconf_ops`, and `sg2042_cfg_ops`.

Control flow: the common Sophgo probe calls this file's init callback, mapping resource 0. DT group parsing is still handled by `sophgo_pctrl_dt_node_to_map()`, but SG2042 does not supply extra verify or post hooks. Mux calls invoke `sg2042_set_pinmux_config()`. Pinconf set computes a value/mask pair, including special pull encoding for `PIN_FLAG_ONLY_ONE_PULL` and output-enable suppression for `PIN_FLAG_NO_OEX_EN`, then calls `sg2042_set_pin_reg()`.

State and persistence: no private logical state beyond the mapped base pointer. Hardware register bits hold mux and pinconf state. Updates are read-modify-write under the common raw spinlock; shared low/high halfword registers are preserved through masks.

Dependencies and integration: depends on `pinctrl-sg2042.h`, Sophgo common helpers, generic pinconf helpers, and SoC-specific VDDIO maps from SG2042/SG2044 files. Risks include flag/table mismatch corrupting the neighboring halfword, unvalidated mux values because no SG2042 verify hook is installed, `INPUT_SCHMITT_ENABLE` only setting enable with no disable path, and output-enable state tied to nonzero drive strength. Test signals include low/high halfword preservation, no-op mux on boot/mode pins, one-pull versus two-bit pull encodings, drive-strength map boundaries, and debugfs pin output showing expected mux/register values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sophgo/pinctrl-sg2042-ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sophgo/pinctrl-sg2042.c -->
## `sources/distributed-fs/ceph-client/drivers/pinctrl/sophgo/pinctrl-sg2042.c`

Purpose: SG2042-specific pin list, table, electrical values, and platform driver binding. It supplies data consumed by the shared SG2042 ops for a broad server-class pin set including LPC, PCIe, SPI flash, eMMC/SDIO, RGMII, PWM/FAN, I2C, UART, SPI, JTAG, GPIO, boot/mode straps, clock inputs, reset, test, and BISR pins.

Important APIs/types/functions: `sg2042_get_pull_up()` and `sg2042_get_pull_down()` return fixed typical pull values of 35k and 28k ohms. `sg2042_oc_map[]` provides 16 output-current steps from 5400 to 45400 microamps via `sg2042_get_oc_map()`. `sg2042_vddio_cfg_ops` exports those conversions. `sg2042_pins[]` lists `PINCTRL_PIN()` descriptors from `dt-bindings/pinctrl/pinctrl-sg2042.h`. `sg2042_pin_data[]` maps every pin to an offset and flags such as `PIN_FLAG_WRITE_HIGH`, `PIN_FLAG_ONLY_ONE_PULL`, `PIN_FLAG_NO_PINMUX`, and `PIN_FLAG_NO_OEX_EN`.

Control flow: the OF match `sophgo,sg2042-pinctrl` selects `sg2042_pindata`, then `sophgo_pinctrl_probe()` registers the shared SG2042 ops. Runtime set-mux and pinconf operations are table-driven by offsets and flags from this file.

State and persistence: immutable pin tables describe register layout; hardware register contents are the only persistent runtime state. Because many adjacent pins share a 32-bit register split into low/high halves, correct `PIN_FLAG_WRITE_HIGH` placement is essential to preserve neighboring pin state.

Dependencies and integration: depends on SG2042 binding constants, `pinctrl-sg2042.h`, and the shared Sophgo/SG2042 ops. Risks are dominated by table correctness and flag semantics: strap/clock/test pins are marked no-mux/no-output-enable, many pins use single-direction pull encoding, and any generated offset error can affect unrelated pins. Test signals include probe with `sophgo,sg2042-pinctrl`, mux/pinconf on low and high halfword pairs, GPIO/pinctrl handoff on PL-style GPIO pins, no mux writes for boot/mode pins, and drive-strength conversion for all 16 map entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sophgo/pinctrl-sg2042.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sophgo/pinctrl-sg2042.h -->
## `sources/distributed-fs/ceph-client/drivers/pinctrl/sophgo/pinctrl-sg2042.h`

Purpose: shared public contract for SG2042-style Sophgo pinctrl tables and ops. It defines flag bits, the per-pin table structure, conversion helper, exported ops, and the table macro used by SG2042 and SG2044 SoC files.

Important APIs/types/functions: flag bits are `PIN_FLAG_WRITE_HIGH`, `PIN_FLAG_ONLY_ONE_PULL`, `PIN_FLAG_NO_PINMUX`, `PIN_FLAG_NO_OEX_EN`, and `PIN_FLAG_IS_ETH`. `struct sg2042_pin` embeds `struct sophgo_pin` and a 16-bit register offset. `sophgo_to_sg2042_pin()` provides container conversion. `SG2042_GENERAL_PIN()` creates table entries. The header exports `sg2042_pctrl_ops`, `sg2042_pmx_ops`, `sg2042_pconf_ops`, and `sg2042_cfg_ops`.

Control flow: no executable flow is present, but the flags defined here directly select behavior in `pinctrl-sg2042-ops.c`: high-halfword read/write, pull encoding format, mux suppression, and output-enable suppression. The macro is the only local constructor for SoC pin metadata.

State and persistence: no mutable state. The struct layout and flag values are compile-time ABI between SG2042-family SoC tables and the shared implementation. `pinsize` in `struct sophgo_pinctrl_data` must match `sizeof(struct sg2042_pin)`.

Dependencies and integration: includes Linux pinctrl/pinconf headers and `pinctrl-sophgo.h`. It is included by SG2042, SG2044, and SG2042 ops source files. Risks include unused or under-documented flags such as `PIN_FLAG_IS_ETH`, future table authors misunderstanding high-halfword sharing, and no compile-time guard that flag combinations make electrical sense. Test signals are build coverage for all macro users, static review of low/high offset pairings, and runtime pinconf tests for each flag combination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sophgo/pinctrl-sg2042.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sophgo/pinctrl-sg2044.c -->
## `sources/distributed-fs/ceph-client/drivers/pinctrl/sophgo/pinctrl-sg2044.c`

Purpose: SG2044-specific data provider for the SG2042-style pinctrl ops. It supplies SG2044 binding IDs, pin names, register offsets, flags, electrical pull values, output-current map, and the `sophgo,sg2044-pinctrl` platform binding.

Important APIs/types/functions: `sg2044_get_pull_up()` returns 19500 ohms, `sg2044_get_pull_down()` returns 23200 ohms, and `sg2044_oc_map[]` provides 16 drive-current steps from 3200 to 51400 microamps through `sg2044_get_oc_map()`. `sg2044_pins[]` includes SMBus sideband pins, PCIe lanes 0-4, SPI flash, eMMC/SDIO, RGMII, PWM/FAN, I2C, UART, SPI, JTAG0-3, GPIO0-31, boot/mode straps, socket IDs, multiple DDR clock inputs, test pins, and BISR. `sg2044_pin_data[]` maps these to SG2042-style offsets and flags. `sg2044_pindata` reuses `sg2042_cfg_ops`, `sg2042_pctrl_ops`, `sg2042_pmx_ops`, and `sg2042_pconf_ops`.

Control flow: OF match `sophgo,sg2044-pinctrl` selects this data, then the shared Sophgo probe and SG2042 ops handle mapping, DT group parsing, mux, and pinconf. This file participates at runtime only through VDDIO callbacks and table lookups.

State and persistence: tables are immutable. Runtime state is in the single SG2044 pinctrl MMIO region. Offset/flag data determines which 16-bit halfword is touched and whether mux/output-enable operations are suppressed.

Dependencies and integration: depends on `dt-bindings/pinctrl/pinctrl-sg2044.h` and the SG2042-family shared header/ops. Risks include copied SG2042 assumptions not matching SG2044 hardware, lack of mux-value validation in shared SG2042 ops, no `PIN_FLAG_ONLY_ONE_PULL` use where hardware might need it, and register-offset drift because the SG2044 table has different layout from SG2042. Test signals include matching `sophgo,sg2044-pinctrl`, pinconf on low/high pairs, strap pins preserving no-mux/no-output-enable behavior, drive map boundary tests, and debugfs pin reports matching expected register offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sophgo/pinctrl-sg2044.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sophgo/pinctrl-sophgo-common.c -->
## `sources/distributed-fs/ceph-client/drivers/pinctrl/sophgo/pinctrl-sophgo-common.c`

Purpose: common Sophgo pinctrl framework code shared by CV18xx and SG2042-style drivers. It provides pin lookup, DT group/function construction, mux dispatch, pinconf dispatch, VDDIO conversion helpers, and the common platform probe.

Important APIs/types/functions: `sophgo_get_pin()` uses `bsearch()` over the SoC `pindata` table using `pinsize`. `sophgo_pctrl_dt_node_to_map()` parses child nodes containing `pinmux`, allocates generic pinctrl maps, validates each pin through optional callbacks, adds groups with pinmux data, parses generic pinconf, and adds a function for the parent node. `sophgo_pmx_set_mux()`, `sophgo_pconf_set()`, and `sophgo_pconf_group_set()` invoke SoC callbacks under locking. Conversion helpers translate pull/down/up, output-current register indexes, and Schmitt thresholds through `vddio_ops`. `sophgo_pinctrl_probe()` allocates `struct sophgo_pinctrl`, initializes locks, calls SoC init, registers the pinctrl device, and enables it.

Control flow: platform drivers provide `struct sophgo_pinctrl_data` through OF match data. During DT map parsing, child groups are converted to `PIN_MAP_TYPE_MUX_GROUP` plus optional `PIN_MAP_TYPE_CONFIGS_GROUP`. During mux set, generic group data is walked and each pin's SoC `set_pinmux_config()` is called. During pinconf set, generic configs become a single value/mask pair and are written per pin.

State and persistence: driver state includes `pctrl->priv_ctrl`, lock/mutex, and registered generic group/function data. Group names, pin arrays, and pinmux arrays are devm-allocated and remain for device lifetime. Hardware register writes persist outside the in-memory data structures.

Dependencies and integration: depends on Linux pinctrl core/generic helpers, OF, bsearch, cleanup guards, and SoC callback contracts from `pinctrl-sophgo.h`. Risks include reliance on sorted `pindata`, group allocations using devm while maps use kzalloc, possible memory leakage on some early `dt_node_to_map` errors, ignoring failures from `sophgo_pin_set_config()` inside group set, and using first group pin to compute group-wide pinconf. Test signals include map creation/free on DT errors, pin lookup for every SoC table entry, group set error propagation expectations, concurrent mux/pinconf lock coverage, and pinctrl enable/probe failures for missing match data or invalid pin count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sophgo/pinctrl-sophgo-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sophgo/pinctrl-sophgo.h -->
## `sources/distributed-fs/ceph-client/drivers/pinctrl/sophgo/pinctrl-sophgo.h`

Purpose: central Sophgo pinctrl interface shared by all Sophgo SoC implementations. It defines generic pin table structures, SoC callback contracts, VDDIO callback contracts, runtime controller state, exported common helper prototypes, and the common probe entry point.

Important APIs/types/functions: `struct sophgo_pin` stores pin ID and flags. `struct sophgo_pin_mux_config` binds a pin pointer to a DT mux config value. `struct sophgo_cfg_ops` defines SoC hooks for initialization, pinmux validation, group validation, DT post-processing, pinconf computation, pinconf writes, and mux writes. `struct sophgo_vddio_cfg_ops` defines electrical conversion hooks. `struct sophgo_pinctrl_data` packages pin descriptors, raw pin data, power-domain names, ops, pin count, power-domain count, and element size. `struct sophgo_pinctrl` stores device, pinctrl descriptors, locks, and SoC private state.

Control flow: SoC platform drivers provide `sophgo_pinctrl_data`; `sophgo_pinctrl_probe()` consumes it and wires generic Linux pinctrl callbacks to SoC-specific behavior. DT parsing and runtime pinctrl requests call the declared common functions, which in turn invoke callback pointers when present.

State and persistence: this header defines but does not allocate state. `mutex` protects DT/group construction; `raw_spinlock_t` protects MMIO register updates. `priv_ctrl` is an opaque pointer owned by the selected SoC backend. `pinsize` is essential for table traversal.

Dependencies and integration: includes Linux device, mutex, platform, spinlock, and pinctrl core headers plus local `../core.h`. It is the contract between common Sophgo code and CV18xx/SG2042 families. Risks include callback pointer assumptions in common code, incomplete ops causing NULL dereferences if a SoC omits required callbacks, `pinsize` mismatch breaking `bsearch()`, and weak compile-time validation of `pindata` ordering. Test signals include build/link coverage for all exported ops, probe with every compatible, invalid pin lookup behavior, and pinconf/mux calls for SoCs with and without optional validation hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sophgo/pinctrl-sophgo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/spacemit/Kconfig -->
## `sources/distributed-fs/ceph-client/drivers/pinctrl/spacemit/Kconfig`

Purpose: build-time configuration entry for the SpacemiT K1/K3 pinctrl driver.

Important APIs/types/functions: `config PINCTRL_SPACEMIT_K1` is a bool option labeled "SpacemiT K1/K3 SoC Pinctrl driver". It depends on `ARCH_SPACEMIT || COMPILE_TEST` and `OF`, defaults to `ARCH_SPACEMIT`, and selects `GENERIC_PINCTRL_GROUPS`, `GENERIC_PINMUX_FUNCTIONS`, and `GENERIC_PINCONF`.

Control flow: no runtime flow. During Kconfig resolution, enabling this symbol causes `drivers/pinctrl/spacemit/Makefile` to build `pinctrl-k1.o`. The help text says the driver allows mux function selection and can also be built as a module called `pinctrl-k1`, although the symbol is declared `bool`, so module build language should be checked against surrounding kernel configuration conventions.

State and persistence: no runtime state. The persistent effect is a kernel build configuration choice.

Dependencies and integration: integrates the driver with architecture selection and compile-test coverage. Risks include the `bool` versus "built as a module" wording mismatch, missing dependency if future code needs clocks/syscon at Kconfig level, and broad default enablement under `ARCH_SPACEMIT`. Test signals include `allyesconfig`/`COMPILE_TEST` build, `ARCH_SPACEMIT` default selection, and verifying selected generic pinctrl helpers are sufficient for `pinctrl-k1.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/spacemit/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/spacemit/Makefile -->
## `sources/distributed-fs/ceph-client/drivers/pinctrl/spacemit/Makefile`

Purpose: build rule for the SpacemiT pinctrl directory.

Important APIs/types/functions: the single object assignment `obj-$(CONFIG_PINCTRL_SPACEMIT_K1) += pinctrl-k1.o` compiles and links the K1/K3 pinctrl implementation when its Kconfig symbol is enabled.

Control flow: no runtime flow. Kbuild expands the `obj-*` variable according to `CONFIG_PINCTRL_SPACEMIT_K1`.

State and persistence: no runtime state; its effect is build artifact inclusion.

Dependencies and integration: integrates the Kconfig symbol with the `pinctrl-k1.c` source file. Risks are limited: if the source is renamed or split, this Makefile must stay synchronized; if Kconfig remains `bool`, no module object will be produced despite help wording. Test signals include incremental build after enabling/disabling `CONFIG_PINCTRL_SPACEMIT_K1` and ensuring no stale object paths are referenced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/spacemit/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/spacemit/pinctrl-k1.c -->
## `sources/distributed-fs/ceph-client/drivers/pinctrl/spacemit/pinctrl-k1.c`

Purpose: complete pinctrl, pinmux, and pinconf driver for SpacemiT K1 and K3 SoCs. It parses DT pinmux groups, registers generic groups/functions, programs MFPR pad registers, handles GPIO request muxing, computes pinconf values including drive strength and slew rate, and optionally switches external IO power-domain voltage through an APBC syscon.

Important APIs/types/functions: `struct spacemit_pinctrl` stores device, pinctrl descriptor/device, locks, MMIO base, and optional APBC regmap. `struct spacemit_pinctrl_data` selects pin descriptors, per-pin data, offset mapping, IO power-domain mapping, and drive config. `spacemit_k1_pin_to_offset()`/`spacemit_k3_pin_to_offset()` map pin IDs to MFPR offsets. `spacemit_pctrl_dt_node_to_map()` parses child `pinmux` arrays and generic pinconf. `spacemit_pmx_set_mux()` writes `PAD_MUX`; `spacemit_request_gpio()` writes each pin's GPIO function. `spacemit_pinconf_generate_config()` handles bias, drive strength, Schmitt, power source, and slew rate. `spacemit_set_io_pwr_domain()` unlocks APBC protected registers with ASFAR/ASSAR keys before voltage changes.

Control flow: probe maps resource 0, optionally looks up `spacemit,apbc`, enables `func` and `bus` clocks, fills the pinctrl descriptor, registers and enables pinctrl. DT parsing builds one mux map and optional config map per child group. Mux set preserves non-mux bits. Pinconf set computes a value word and `spacemit_pin_set_config()` writes it while preserving the current mux. Group pinconf computes from the first pin and applies the same value to all group pins.

State and persistence: runtime state is the MMIO pad register block, optional APBC voltage-domain registers, enabled clocks, generic pinctrl group/function tables, mutex, and raw spinlock. External IO voltage changes persist in hardware and are only made when drive strength is configured with a valid `power-source`.

Dependencies and integration: depends on Linux clk, regmap/syscon, pinctrl core/generic helpers, OF, and local `pinctrl-k1.h`. OF compatibles are `spacemit,k1-pinctrl` and `spacemit,k3-pinctrl`; required clocks are `func` and `bus`; optional phandle is `spacemit,apbc`. Risks include `if (!pin)` rejecting pin 0 in pinconf paths, DT map error paths returning without freeing allocated maps, `spacemit_request_gpio()` overwriting non-mux config bits, group pinconf using first-pin voltage/type assumptions, and voltage switching being unavailable if APBC syscon is absent. Test signals include probe with/without APBC phandle, K1 and K3 offset mapping spot checks, pin 0 pinconf negative test, external IO `power-source` validation, drive-strength table rounding, slew-rate conflict rejection, and GPIO request preserving expected pad configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/spacemit/pinctrl-k1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/spacemit/pinctrl-k1.h -->
## `sources/distributed-fs/ceph-client/drivers/pinctrl/spacemit/pinctrl-k1.h`

Purpose: local header for SpacemiT K1/K3 pinctrl data construction. It defines IO type encoding, standard voltage constants, and the macro used to create per-pin table entries.

Important APIs/types/functions: `enum spacemit_pin_io_type` distinguishes no IO, fixed 1.8V, fixed 3.3V, and external voltage pins. `PIN_POWER_STATE_1V8` and `PIN_POWER_STATE_3V3` define DT voltage values. `K1_PIN_IO_TYPE`, `K1_PIN_CAP_IO_TYPE()`, and `K1_PIN_GET_IO_TYPE()` encode/decode IO type in pin flags. `K1_FUNC_PIN()` constructs entries containing pin ID, GPIO mux function, and encoded IO type.

Control flow: no runtime flow. The generated/static arrays in `pinctrl-k1.c` rely on these macros and constants to define behavior later used by mux and pinconf code.

State and persistence: no mutable state. The encoded flags become immutable per-pin metadata, and `gpiofunc` values are later written to hardware during GPIO request.

Dependencies and integration: includes Linux bitfield, device, lock, platform, and pinctrl headers. It is private to the SpacemiT driver. Risks include encoding only two bits for IO type, no compile-time validation of macro arguments, and sharing `PIN_POWER_STATE_*` names with other pinctrl families if headers are combined. Test signals include build coverage of all `K1_FUNC_PIN()` users, debug output showing correct IO type descriptions, and pinconf tests for fixed versus external IO behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/spacemit/pinctrl-k1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/spear/Kconfig -->
## `sources/distributed-fs/ceph-client/drivers/pinctrl/spear/Kconfig`

Purpose: Kconfig integration for STMicroelectronics SPEAr pinctrl and PLGPIO support.

Important APIs/types/functions: the menu is gated by `if PLAT_SPEAR`. `PINCTRL_SPEAR` is the common bool depending on `OF` and selecting `PINMUX`. `PINCTRL_SPEAR3XX` depends on `ARCH_SPEAR3XX` and selects the common driver. SoC symbols `PINCTRL_SPEAR300`, `PINCTRL_SPEAR310`, `PINCTRL_SPEAR320`, `PINCTRL_SPEAR1310`, and `PINCTRL_SPEAR1340` depend on their machine symbols and select appropriate common/PLGPIO support. `PINCTRL_SPEAR_PLGPIO` depends on `GPIOLIB && PINCTRL_SPEAR` and selects `GPIOLIB_IRQCHIP`.

Control flow: no runtime flow. Kconfig choices control which common, SoC-specific, and PLGPIO objects are built.

State and persistence: no runtime state; persistent effect is build configuration.

Dependencies and integration: connects legacy SPEAr platform symbols to pinctrl and GPIO infrastructure. Risks include the whole menu being hidden outside `PLAT_SPEAR`, limiting compile-test exposure, and platform-specific selections making dead-code build regressions easier to miss. Test signals include SPEAr defconfig builds, each machine symbol selecting expected objects, and build coverage for PLGPIO IRQ support when selected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/spear/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/spear/Makefile -->
## `sources/distributed-fs/ceph-client/drivers/pinctrl/spear/Makefile`

Purpose: Kbuild object list for SPEAr pinctrl drivers.

Important APIs/types/functions: `obj-y += pinctrl-spear.o` builds the common SPEAr helper whenever this directory is included. Conditional objects include `pinctrl-plgpio.o`, `pinctrl-spear3xx.o`, and SoC files for SPEAr300/310/320/1310/1340 according to Kconfig symbols.

Control flow: no runtime flow. Build inclusion is controlled by `CONFIG_PINCTRL_SPEAR_*` symbols.

State and persistence: no runtime state; it affects the kernel image contents.

Dependencies and integration: ties Kconfig to source files in this directory. Because common `pinctrl-spear.o` is unconditional within the directory, directory-level inclusion must already be constrained by higher-level Makefiles/Kconfig. Risks include stale object entries if SoC files are removed, unconditional common object build without matching platform data in unusual build combinations, and limited compile-test if the directory is not entered. Test signals include SPEAr platform builds and verifying each selected SoC symbol pulls exactly its common prerequisites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/spear/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/spear/pinctrl-plgpio.c -->
## `sources/distributed-fs/ceph-client/drivers/pinctrl/spear/pinctrl-plgpio.c`

Purpose: SPEAr PLGPIO controller driver providing GPIO and optional IRQ support for platform GPIO blocks whose register bit layout may not map one-to-one with logical pin numbers.

Important APIs/types/functions: `struct plgpio_regs` stores register offsets for enable, write data, direction, read data, interrupt enable, masked interrupt status, and edge interrupt type. `struct plgpio` stores lock, regmap, optional clock, `gpio_chip`, optional pin/offset conversion callbacks, register mask, register offsets, and suspend context. GPIO methods include `plgpio_request()`, `plgpio_free()`, direction input/output, get, and set. IRQ methods include `plgpio_irq_enable()`, `plgpio_irq_disable()`, `plgpio_irq_set_type()`, and `plgpio_irq_handler()`. `spear310_p2o()`/`spear310_o2p()` handle non-linear SPEAr310 mapping. PM methods save/restore register context.

Control flow: probe obtains a regmap from a `regmap` phandle or its own DT node, parses `st-plgpio,*` register properties and `ngpio`, prepares an optional clock, sets up GPIO chip methods, optionally wires a chained IRQ parent, and registers the gpiochip. GPIO request also requests pinctrl ownership, enables the clock, defaults the line to input, and sets enable bits. IRQ handling scans MIS registers, clears pending bits, remaps offsets if required, and dispatches domain IRQs.

State and persistence: runtime state includes regmap-backed GPIO registers, clock prepare/enable state, optional IRQ domain state via gpiolib, and suspend snapshots in `csave_regs`. Hardware state is preserved over sleep by explicit save/restore, with last-register masking to avoid overwriting non-PLGPIO bits.

Dependencies and integration: depends on gpiolib, gpiolib irqchip helpers, pinctrl consumer API, clk, OF, regmap/syscon, and platform driver registration. Risks include `REG_OFFSET()` using `sizeof(int *)`, which is pointer-size-dependent, interrupt clear semantics using `~pending`, SPEAr310 remap edge cases, returning from `plgpio_free()` before clock disable if p2o fails, and limited trigger support when no EIT register exists. Test signals include DT parse failures for missing mandatory offsets, GPIO request/free with clock counts, SPEAr310 remap cases, IRQ rising/falling configuration, last partial MIS register masking, and suspend/resume register preservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/spear/pinctrl-plgpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/spear/pinctrl-spear.c -->
## `sources/distributed-fs/ceph-client/drivers/pinctrl/spear/pinctrl-spear.c`

Purpose: common SPEAr pinmux driver core used by SoC-specific SPEAr machine-data files. It exposes pinctrl groups/functions, parses SPEAr DT mux requests, configures optional global pinmux mode, applies mux register tables, and handles GPIO-mode mux enable/disable.

Important APIs/types/functions: `muxregs_endisable()` read-modify-writes arrays of `struct spear_muxreg`. `set_mode()` selects a `struct spear_pmx_mode` from machine data based on DT `st,pinmux-mode`. `pmx_init_addr()` and `pmx_init_gpio_pingroup_addr()` patch placeholder mux register addresses in machine data. Pinctrl ops expose group count/name/pins and parse DT children containing `st,function` and `st,pins`. Pinmux ops expose function count/name/groups and call `spear_pinctrl_endisable()` from `set_mux()`. `gpio_request_endisable()` applies GPIO pingroup mux settings and optional SoC callback. `spear_pinctrl_probe()` maps regmap, sets mode, initializes descriptor pins, and registers pinctrl.

Control flow: SoC drivers call `spear_pinctrl_probe()` with populated `struct spear_pinctrl_machdata`. If modes are supported, probe reads `st,pinmux-mode` and programs the corresponding mode register. DT map creation counts child pin strings, allocates mux maps, and assigns function/group pairs. Runtime mux set walks the selected group's `modemuxs`, filters by current mode if applicable, and applies mux register masks.

State and persistence: `struct spear_pmx` stores device, pinctrl device, machine data, and regmap. `machdata->mode` is updated at probe. Hardware mux registers hold persistent state until changed or reset. Static `spear_pinctrl_desc` is reused across probes, so multi-instance assumptions should be treated carefully.

Dependencies and integration: depends on syscon/device-node regmap, OF, pinctrl core, and SPEAr machine data from sibling SoC files. Risks include static descriptor mutation for multiple controllers, no strict mode in `pinmux_ops`, DT map allocation requiring caller cleanup, and mux disable writing inverse table values that must be correct for every SoC table. Test signals include mode selection failures, DT child parsing for multiple groups, mux register enable/disable readbacks, GPIO request/free toggling pingroup muxes, and SoC table placeholder address initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/spear/pinctrl-spear.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/spear/pinctrl-spear.h -->
## `sources/distributed-fs/ceph-client/drivers/pinctrl/spear/pinctrl-spear.h`

Purpose: shared data model and helper macros for SPEAr pinmux machine-data drivers plus declarations for the common SPEAr probe/helper functions.

Important APIs/types/functions: `struct spear_pmx_mode` describes global pinmux modes. `struct spear_muxreg` describes one masked register write. `struct spear_gpio_pingroup` models GPIO mux groups. Macros `DEFINE_MUXREG`, `DEFINE_2_MUXREG`, and `GPIO_PINGROUP` create common table fragments. `struct spear_modemux`, `struct spear_pingroup`, and `struct spear_function` describe mux possibilities. `struct spear_pinctrl_machdata` aggregates pins, functions, groups, GPIO pingroups, optional GPIO callback, and optional mode data. `struct spear_pmx` stores runtime device, pinctrl device, machine data, and regmap. Inline `pmx_readl()`/`pmx_writel()` wrap regmap access. Pin macros `SPEAR_PIN_0_TO_101` and `SPEAR_PIN_102_TO_245` define PLGPIO pin descriptors.

Control flow: no direct runtime flow except inline regmap wrappers. The structures in this header drive `pinctrl-spear.c` runtime behavior: group/function enumeration, mux application, mode filtering, and GPIO mux handling.

State and persistence: no mutable state is allocated here. It defines the shape of SoC static machine data and the runtime `spear_pmx` container. Placeholder register values may be patched by `pmx_init_addr()` before use.

Dependencies and integration: depends on Linux gpio, io, pinctrl, regmap, and types headers. It is consumed by common SPEAr code and SoC-specific table files. Risks include typo-prone table macros, comments with misspellings but clear meaning, no type-level validation that groups/functions reference each other consistently, and very large pin descriptor macros that can hide ordering mistakes. Test signals include compile coverage of all SoC table users, pin/group/function enumeration checks, regmap read/write tracing, and validation that GPIO pin numbering matches PLGPIO chip numbering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/spear/pinctrl-spear.h -->
