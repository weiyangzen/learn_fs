# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_dsa.h

Purpose: Defines the public Prestera DSA tag contract shared by RX/TX code.

Important APIs/types/functions: `PRESTERA_DSA_HLEN` fixes tag length at 16 bytes. `enum prestera_dsa_cmd` defines TO_CPU and FROM_CPU command values. `struct prestera_dsa_vlan` carries VID, priority, CFI, and tagged status. `struct prestera_dsa` carries VLAN metadata, hardware device number, port number, and CPU code. Declares parse/build functions.

Control flow: Consumers allocate/populate `struct prestera_dsa`, then call parse for ingress tags or build for egress tags. The header has no inline control flow.

State and persistence: No state. It defines transient packet metadata only.

Dependencies/integration: Included by the DSA implementation and packet datapath. The CPU code field integrates with devlink trap reporting and hardware trap metadata.

Risks: The tag length and struct interpretation must match the firmware/hardware DSA format. Any enum or field expansion must preserve existing ABI expectations in parser/build logic.

Test signals: Compile-time users in RX/TX, packet round-trip tests, and assertions that callers reserve/consume exactly `PRESTERA_DSA_HLEN` bytes.
