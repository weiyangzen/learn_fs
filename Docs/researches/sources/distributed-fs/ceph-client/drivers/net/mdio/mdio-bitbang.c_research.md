<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-bitbang.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-bitbang.c

Purpose: implements MDIO Clause 22 and Clause 45 protocol bit-banging over controller-specific pin operations.

Important APIs/types/functions: exported APIs are `mdiobb_read_c22`, `mdiobb_write_c22`, `mdiobb_read_c45`, `mdiobb_write_c45`, `alloc_mdio_bitbang`, and `free_mdio_bitbang`. It depends on `struct mdiobb_ctrl` and `struct mdiobb_ops` for MDC/MDIO direction, data set, and data get callbacks.

Control flow: helper routines send bits and numbers with timing delays, emit preamble/start/opcode/PHY/register fields, perform Clause 45 address phases, handle turnaround, and read/write 16-bit payloads. Allocation creates a `mii_bus`, pins callbacks to the exporting module, installs C22/C45 read/write callbacks, and initializes default C22 opcodes unless overridden.

State and persistence: state is owned by the embedding controller in `mdiobb_ctrl`; the library only allocates/frees an mii_bus and holds a module reference on ops owner. No hardware state is stored here.

Dependencies/integration: used by GPIO and other low-level drivers that can drive MDIO pins. It integrates with phylib through standard mii_bus callbacks and supports `phy_ignore_ta_mask`.

Risks and test signals: risks include timing margins on slow GPIO providers, sleeping GPIO callbacks under bus locks, turnaround handling returning `0xffff`, and module owner reference imbalance. Tests should cover C22/C45 waveforms, overridden C22 opcodes, broken TA masks, and alloc/free module references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-bitbang.c -->
