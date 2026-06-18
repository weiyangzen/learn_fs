<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/cps-vec-ns16550.S -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/cps-vec-ns16550.S

### Purpose
This assembly file provides a stackless early UART diagnostic path for MIPS CPS BEV exceptions using an NS16550-compatible UART.

### Important APIs, Types, And Functions
Important symbols are `_mips_cps_putc`, `_mips_cps_puts`, `_mips_cps_putx4`, `_mips_cps_putx8`, `_mips_cps_putx16`, `_mips_cps_putx32`, `_mips_cps_putx64` on 64-bit, and `mips_cps_bev_dump`.

### Control Flow
Low-level putc polls UART line status until transmit-empty, then writes the character. Hex helpers recursively emit nibbles/bytes/words. `mips_cps_bev_dump()` builds the UART base from config, prints the exception name, and dumps CP0 Cause, Status, EBase, BadVAddr, and BadInstr.

### State, Persistence, And Dependencies
State is only registers and UART MMIO; the code intentionally avoids stack and normal memory. Dependencies are `CONFIG_MIPS_CPS_NS16550_*` width, shift, and base settings plus serial register definitions.

### Integration Points
`cps-vec.S` invokes `mips_cps_bev_dump` through the `DUMP_EXCEP` macro when configured, helping debug very early CPS core bring-up failures.

### Risks
Wrong UART base/width/shift can hang or print garbage during fatal exception handling. The code uses callee-saved registers without normal ABI stack preservation because it runs in emergency context.

### Test Signals
Force early BEV exception on a CPS system with configured UART, verify readable register dump, and build-test 8/16/32-bit UART width and 32/64-bit kernels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/cps-vec-ns16550.S -->
