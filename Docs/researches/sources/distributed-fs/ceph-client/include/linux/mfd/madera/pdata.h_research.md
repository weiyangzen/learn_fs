# Research: sources/distributed-fs/ceph-client/include/linux/mfd/madera/pdata.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/madera/pdata.h -->
## sources/distributed-fs/ceph-client/include/linux/mfd/madera/pdata.h

**Purpose:** Defines board/platform configuration data for Madera codec MFD devices, bridging regulator, pinctrl/GPIO, interrupt, general-purpose switch, and ASoC codec configuration.

**Important APIs and types:** `struct madera_pdata` includes reset GPIO, Arizona-compatible LDO1 and MICVDD regulator pdata, IRQ flags, legacy GPIO base, pinctrl maps and count, two GPSW mode values, and `struct madera_codec_pdata`.

**Control flow:** Parent probe imports firmware or board data into `madera_pdata`, then child regulator, GPIO/pinctrl, and codec drivers read their slices during registration.

**State and persistence:** This is configuration state copied into `struct madera`; it does not itself own runtime resources except referenced descriptors/maps.

**Dependencies and integration:** Includes Arizona regulator pdata headers, regulator machine constraints, Linux types, and `sound/madera-pdata.h`.

**Risks:** Mixed legacy and descriptor-based GPIO configuration can create board-specific corner cases. `gpio_configs` and `n_gpio_configs` must remain consistent. GPSW values are raw datasheet mode fields with no enum validation here.

**Test signals:** Probe tests with no reset GPIO, DT/ACPI-to-pdata conversion checks, pinctrl map count validation, regulator pdata handoff checks, and codec child tests using populated and empty `codec` data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/madera/pdata.h -->
