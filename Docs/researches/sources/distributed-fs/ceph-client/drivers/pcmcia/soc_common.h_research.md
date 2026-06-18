# sources/distributed-fs/ceph-client/drivers/pcmcia/soc_common.h

Purpose: Defines the private common interface used by SoC PCMCIA socket drivers.

Important APIs and types: Defines `struct skt_dev_info` as a flexible array of `soc_pcmcia_socket`, `struct soc_pcmcia_timing` with I/O/memory/attribute access times, public common helper prototypes, debug macro plumbing, default access timing constants, polling period, and aliases `iostschg`/`iospkr` for I/O-card signal semantics.

Control flow: No executable logic except debug macro expansion. The prototypes form the boundary between low-level board drivers and `soc_common.c`.

State and persistence: The header defines container shapes for per-device socket allocation and timing values; persistent hardware state is managed by users.

Dependencies and integration points: Includes Linux clock/cpufreq and PCMCIA SoC/CIS headers, and is included by PXA2xx, SA11xx, SA1111, and board-specific files.

Risks: Timing constants encode PC Card spec assumptions and drive SoC memory-controller programming. `struct skt_dev_info` flexible allocation requires correct size calculation. Debug macro availability depends on `CONFIG_PCMCIA_DEBUG`.

Test signals: Compile coverage of all SoC socket drivers and runtime timing defaults when no explicit map speed is supplied.
