# sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/ksz8.h

Purpose: internal KSZ8-family operation declarations used by Microchip KSZ common code and transports.

Important APIs/types/functions: declares setup, port address, membership, dynamic MAC flush, port setup, PHY access, MIB access, FDB/MDB, VLAN, mirror, phylink caps/link-up, CPU-port config, STP address programming, reset/init/exit, MTU change, PME access, queue split, and KSZ8463-specific helpers.

Control flow: no runtime flow; declarations connect KSZ8 implementation to common operation tables.

State and persistence: no direct state; all functions operate on `struct ksz_device`, `struct dsa_switch`, phylink, or switchdev objects.

Dependencies and integration: includes `ksz_common.h`, DSA types, and Linux types. Used by `ksz8.c` and `ksz8863_smi.c`.

Risks and test signals: signature drift with operation tables or missing hooks. Build all KSZ8-related transports and common code.
