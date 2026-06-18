# sources/distributed-fs/ceph-client/arch/mips/ralink/prom.c

Purpose: common Ralink PROM entry code. It owns the global `soc_info` and `ralink_soc` state, reports the system type, and imports bootloader command-line arguments into `arcs_cmdline`.

Important APIs and control flow: `prom_init()` calls the SoC-family implementation of `prom_soc_init(&soc_info)`, logs `get_system_type()`, and then runs `prom_init_cmdline()`. The command-line parser treats `fw_arg0` as argc and `fw_arg1` as a KSEG1 argv pointer, appending non-empty physical addresses to `arcs_cmdline`.

State, persistence, and integration: persistent boot state is the global SoC descriptor plus the final kernel command line. It depends on bootloader argument layout, `KSEG1ADDR()` conversion, and one selected SoC object file exporting `prom_soc_init()`. Risks include trusting firmware pointers and silent command truncation through `strlcat()`. Test signals include "SoC Type" logging, expected `/proc/cpuinfo` system type, and boot arguments appearing in `/proc/cmdline`.
