# sources/distributed-fs/ceph-client/arch/m68k/mac/config.c

## Purpose
Provides central Macintosh m68k platform configuration: bootinfo parsing, machdep hook wiring, model identification, hardware feature tables, early chip initialization, and platform-device registration.

## APIs, Flow, And State
Important globals are `struct mac_booter_data mac_bi_data`, `struct mac_model *macintosh_config` exported to drivers, and exported SCC platform devices `scc_a_pdev` and `scc_b_pdev`. `mac_parse_bootinfo()` decodes Mac-specific bootinfo tags into `mac_bi_data`. `config_mac()` installs `mach_sched_init`, `mach_init_IRQ`, `mach_get_model`, `mach_hwclk`, reset, halt, and optional beep hooks, then calls `mac_identify()` and reports the selected model. `mac_identify()` selects an entry from `mac_data_table`, prepares SCC MMIO/IRQ resources, logs booter video/time/memory data, and initializes IOP, OSS, VIA, PSC, Baboon, CUDA, and PMU discovery. `mac_platform_init()` is an `arch_initcall` registering SCC, SWIM floppy, SCSI, IDE, and Ethernet platform devices based on table fields.

## Dependencies And Integration
Depends on m68k setup, bootinfo, machdep, Mac IRQ, VIA/OSS/PSC/IOP, ADB/CUDA/PMU, platform device, ATA, RTC, and model constants. It is the integration point for Mac board files and for legacy drivers such as `mac_scsi`, `mac_esp`, `pata_platform`, `macsonic`, `mac89x0`, and `macmace`.

## Risks And Test Signals
The hardcoded model table includes comments about guesswork; incorrect feature classification can crash early MMIO probing or register wrong devices. Address resources are model-specific and historically subtle. Test signals are boot logs showing detected model and booter data, correct serial console resources, successful platform-device probing, and power/reset/clock operations on representative II, Quadra, AV, and PowerBook systems.
