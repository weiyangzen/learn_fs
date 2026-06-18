## sources/distributed-fs/ceph-client/arch/mips/pic32/pic32mzda/init.c

### Purpose
This file contains PIC32MZDA machine initialization: system-type reporting, early device-tree setup, command-line construction, early console/config init, SDHCI auxdata, and OF platform population.

### Important APIs, Types, And Functions
`get_system_type()` returns `"PIC32MZDA"`. `plat_mem_setup()` obtains the FDT, calls `__dt_setup_arch()`, logs command lines, initializes early console and config registers. `pic32_init_cmdline()` builds `arcs_cmdline` from firmware arguments. `prom_init()` calls that parser. `pic32_auxdata_lookup[]` supplies SDHCI platform data with `pic32_set_sdhci_adma_fifo_threshold`. `pic32_of_prepare_platform_data()` fills auxdata names/addresses from DT. `plat_of_setup()` populates OF devices.

### Control Flow
Firmware args are captured in `prom_init()`. `plat_mem_setup()` runs early, loads DT memory/chosen data, copies command line when using an external DTB, initializes optional early console, and calls `pic32_config_init()`. At `arch_initcall()`, `plat_of_setup()` requires a populated DT, prepares auxdata, and calls `of_platform_default_populate()`.

### State, Persistence, And Dependencies
State includes boot command lines, OF device population, SDHCI platform data, and config initialization side effects. Dependencies include firmware FDT access, Linux OF APIs, PIC32 config/early-console helpers, and SDHCI PIC32 platform data.

### Integration Points
This is the central link between firmware, built-in/external DTB, early printk, platform devices, and PIC32-specific SDHCI DMA setup.

### Risks
No DTB only logs an error in `plat_mem_setup()`, but later `plat_of_setup()` panics if no populated DT exists. Command-line concatenation silently truncates. Auxdata lookup mutates names from DT and assumes first resource is the device base.

### Test Signals
Boot with built-in and external DTBs, confirm memory discovery, command-line logs, SDHCI auxdata setup, OF platform devices, and early console ordering.
