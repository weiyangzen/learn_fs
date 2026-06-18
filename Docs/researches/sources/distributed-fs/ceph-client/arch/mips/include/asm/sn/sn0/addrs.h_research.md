<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/sn0/addrs.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/sn0/addrs.h

Purpose: Defines SN0/IP27-specific NASID geometry, node/window address layout, PROM memory map, UART/I2C addresses, cache-error frame locations, and error-workaround addresses.

Important APIs/types/functions: `NODE_SIZE_BITS`, `NASID_*`, `NODE_SWIN_BASE`, big-window helpers `NODE_BWIN_BASE`, `NODE_BWIN_ADDR`; PROM constants `IP27PROM_*`, `IO6PROM_*`; local UART/I2C register bases; cache-error offsets; and error workaround macros such as `ERR_STS_WAR_ADDR`.

Control flow: Generic SN address macros include this file to get SN0-specific bit shifts and boot memory map. Boot and PROM code use the constants to locate firmware entry points, launch loops, stacks, console buffers, flash/diagnostic areas, and local hub I/O registers.

State and persistence: The header describes fixed physical layout and PROM-reserved persistent areas. It owns no variables but points code at memory/register regions with boot-critical meaning.

Dependencies and integration points: Depends on MIPS address-space conversion macros through includers and on hub register constants for workaround addresses.

Risks: Many constants are physical addresses used before full MMU setup; mistakes can overwrite PROM, stacks, or diagnostic buffers. N-mode versus M-mode geometry changes NASID/node size semantics.

Test signals: IP27 PROM handoff, early console, secondary launch, KLDIR/GDA discovery, and cache-error handling tests are relevant.

Source read size: 283 lines, 9296 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/sn0/addrs.h -->
