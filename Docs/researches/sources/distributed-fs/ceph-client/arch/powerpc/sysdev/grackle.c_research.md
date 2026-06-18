<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/grackle.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/grackle.c

Purpose: Sets up the MPC106/Grackle PCI host bridge and applies PowerMac-specific configuration quirks.

Important APIs/types/functions: Provides `setup_grackle()`, with helper `grackle_set_loop_snoop()` and config address macro `GRACKLE_CFA()`.

Control flow: `setup_grackle()` configures indirect PCI access at fixed Grackle config address/data windows. It enables all-bus reassignment on `PowerMac1,1` and turns on PICR1 loop snoop on `AAPL,PowerBook1998` by writing config register `0xa8`.

State and persistence: Persistent state is PCI host-controller config address/data mappings installed by `setup_indirect_pci()` and the hardware PICR1 loop-snoop bit.

Dependencies and integration points: Depends on indirect PCI helpers, OF machine compatibility checks, PCI reassignment flags, and Grackle host bridge platform setup.

Risks: Fixed physical config windows are platform-specific. The loop-snoop quirk is a hardware erratum workaround and must remain narrowly scoped to the affected PowerBook model.

Test signals: Old PowerMac/PowerBook boot, PCI enumeration through indirect config access, bus reassignment on PowerMac1,1, and loop-snoop register verification on PowerBook1998.

Source read size: 43 lines, 1274 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/grackle.c -->
