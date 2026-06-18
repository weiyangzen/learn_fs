# sources/distributed-fs/ceph-client/arch/mips/include/asm/sgiarcs.h

## sources/distributed-fs/ceph-client/arch/mips/include/asm/sgiarcs.h

### Purpose
`sgiarcs.h` defines the SGI ARC/ARCS firmware ABI: error codes, device-tree component classes/types/identifiers, memory descriptors, file/time/directory structures, ROM vector layout, system parameter block, boot blocks, debugger block, cache/config data, and ARC call wrappers for 32-bit and 64-bit firmware combinations.

### Important APIs, Types, And Functions
Major types include `enum linux_devclass`, `enum linux_devtypes`, `enum linux_identifier`, `struct linux_component`, `struct linux_sysid`, ARCS/ARC memory type enums, `struct linux_mdesc`, `struct linux_tinfo`, `struct linux_vdirent`, `enum linux_omode`, `enum linux_seekmode`, `enum linux_mountops`, `struct linux_bigint`, `struct linux_finfo`, `struct linux_romvec`, `SYSTEM_PARAMETER_BLOCK`, `union linux_cache_key`, `struct linux_cdata`, `struct sgi_partition`, `struct sgi_bootblock`, `struct sgi_bparm_block`, `struct sgi_bsector`, and `struct linux_smonblock`. Important macros include `PROM_E*`, `PROMBLOCK`, `ROMVECTOR`, `SGIPROM_*`, boot block constants, `SMB_DEBUG_MAGIC`, and `ARC_CALL0` through `ARC_CALL5`.

### Control Flow
Firmware clients access the fixed `PROMBLOCK`, retrieve the ROM vector, and invoke function pointers through `ARC_CALL*`. On 64-bit kernels calling 32-bit ARC firmware, wrappers funnel calls through `call_o32` and a dedicated O32 stack; matching-width kernels call function pointers directly.

### State, Persistence, Dependencies, And Integration
State is firmware-owned PROM structures, ROM vector functions, environment variables, memory descriptors, firmware file descriptors, boot blocks, and debugger metadata. Persistent data may include firmware environment and boot media metadata, but the header itself only defines layouts. Dependencies include kernel helpers, MIPS/ARC fixed-width types, endianness macros, and `ARRAY_SIZE` in call-wrapper code.

### Risks
The ABI is firmware-defined; struct packing, pointer width, endianness of `linux_bigint`, and 32/64-bit call conventions must be exact. The fixed PROM block address is unmapped or invalid outside SGI ARCS boot contexts. Wrong call wrappers can corrupt firmware stack/register state.

### Test Signals
Boot 32-bit and 64-bit SGI ARCS configurations, call representative firmware services through `ARC_CALL*`, validate memory descriptors/environment/file I/O, inspect boot partition parsing, and test ARC32-on-64-bit wrapper stack behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sgiarcs.h -->
