# sources/distributed-fs/ceph-client/arch/mips/include/asm/sgialib.h

## sources/distributed-fs/ceph-client/arch/mips/include/asm/sgialib.h

### Purpose
`sgialib.h` declares the SGI ARCS firmware helper library used during MIPS SGI boot for console I/O, memory descriptors, firmware environment, command-line parsing, file I/O, display status, and PROM mode transitions.

### Important APIs, Types, And Functions
Exports include global `romvec`, `prom_flags`, flags `PROM_FLAG_ARCS`, `PROM_FLAG_USE_AS_CONSOLE`, `PROM_FLAG_DONT_FREE_TEMP`, `prom_getchar`, `prom_getmdesc`, `PROM_NULL_MDESC`, `prom_meminit`, `PROM_NULL_COMPONENT`, `prom_identify_arch`, `ArcGetEnvironmentVariable`, `prom_init_cmdline`, `ArcRead`, `ArcWrite`, `ArcEnterInteractiveMode`, and `ArcGetDisplayStatus`.

### Control Flow
Early SGI boot initializes `romvec`, identifies firmware architecture, reads memory descriptors into kernel memory setup, parses ARCS command-line/environment values, and optionally uses PROM console/file/display services before normal drivers take over.

### State, Persistence, Dependencies, And Integration
State is firmware ROM vector pointer, PROM flags, ARCS memory descriptors, environment variables, file handles, and display status. Dependencies include compiler attributes and `sgiarcs.h`. Integration is with SGI PROM boot, memory initialization, early console, initrd/boot file loading, and architecture identification.

### Risks
Firmware calls may be 32-bit or 64-bit depending on ARCS mode and must match the wrappers in `sgiarcs.h`. PROM memory marked temporary or permanent must not be freed incorrectly. Early console use can conflict with later drivers if flags are wrong.

### Test Signals
Boot SGI ARCS systems, compare memory map from PROM with Linux memblock, read environment variables and command line, test PROM console/file reads early, and verify no calls occur after firmware services are unsafe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sgialib.h -->
