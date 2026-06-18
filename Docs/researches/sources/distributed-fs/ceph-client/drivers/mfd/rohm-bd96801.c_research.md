# sources/distributed-fs/ceph-client/drivers/mfd/rohm-bd96801.c

### Purpose
`rohm-bd96801.c` is the MFD parent for ROHM BD96801, BD96802, BD96805, and BD96806 scalable PMICs. It provides basic PMIC unlock, regmap setup, INTB/ERRB interrupt controller setup, watchdog and regulator child registration, and child IRQ resource mapping. The driver explicitly does not implement STBY-state safety-limit configuration because that requires system-specific coordination of PMIC state transitions.

### Important APIs, Types, And Functions
The main entry point is `bd96801_i2c_probe()`. `struct bd968xx` is the chip descriptor carrying INTB/ERRB resource arrays, regmap IRQ chips, regmap config, MFD cells, and unlock register/value. Static chip descriptors are `bd96801_data`, `bd96802_data`, `bd96805_data`, and `bd96806_data`. IRQ topology is represented by resource arrays, regmap IRQ arrays, sub-IRQ maps, and four IRQ chips: BD96801/BD96802 INTB and ERRB.

### Control Flow
Probe selects a descriptor from device match data, requires a firmware node and a named `intb` IRQ, optionally accepts a named `errb` IRQ unless it is deferred, allocates a combined regulator resource array sized to INTB plus optional ERRB resources, creates the I2C regmap, writes the PMIC unlock value, and registers the INTB regmap IRQ chip. Because MFD core only accepts one IRQ domain, the driver maps each child IRQ itself with `irq_create_mapping()` and stores concrete Linux IRQ numbers in the regulator resource array. It also maps the watchdog error IRQ from INTB and stores it in the watchdog cell. If ERRB exists, a second regmap IRQ chip/domain is registered and its events are appended to regulator resources. Finally, watchdog and regulator children are added without passing an IRQ domain.

### State, Persistence, And Dependencies
Runtime state is largely device-managed regmap, IRQ chip data, mapped IRQ resources, and child devices. Persistent hardware state includes the unlock register write and IRQ mask/ack programming. Regmap volatile tables deliberately include status registers and STBY-only configuration registers whose writes may not latch unless the PMIC is in standby; this reduces stale regcache risks. Dependencies include I2C, firmware-node named IRQs, regmap, regmap-irq, MFD core, IRQ domain mapping, and ROHM BD96801/BD96802 register headers.

### Integration Points
The watchdog child is `bd96801-wdt` or `bd96806-wdt`; regulator child names are chip-specific. Regulator children receive concrete IRQ resources from both INTB and optional ERRB lines, including regulator overcurrent, over/under-voltage, thermal warning, shutdown, and fatal fault resources. Systems that wire only INTB still get nonfatal regulator/thermal events; systems that wire ERRB get additional fatal fault reporting if the SoC remains alive.

### Risks
INTB and ERRB share the same main status register. The source comments call out that simultaneous INTB/ERRB assertions for different sub-status offsets could make regmap-irq read a sub-status register with no active bits and potentially return repeated `IRQ_NONE`. ERRB may be omitted on systems powered by the PMIC, so fatal fault observability can be absent by design. Several chip variants reuse descriptor data from BD96801 or BD96802; mismatched register maps or resources would break event routing. `bd96806_data` is non-const while the others are const, and static MFD cell resource mutation can be sensitive to multiple instances.

### Test Signals
Probe tests should cover all four compatibles, required `intb`, optional `errb`, ERRB `-EPROBE_DEFER`, unlock write failure, and MFD creation. IRQ tests should confirm INTB and ERRB resource mapping produces usable Linux IRQs for watchdog and regulator children, with BD96801/BD96805 seven-regulator maps and BD96802/BD96806 two-regulator maps. Regcache tests should verify volatile STBY-only and status ranges are not stale. Hardware tests should inject thermal, overcurrent, OVD/UVD, watchdog, and fatal ERRB events where safe.
