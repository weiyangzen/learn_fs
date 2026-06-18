# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/global1_vtu.c

Purpose: implements VLAN Translation Unit and Spanning Tree Unit operations, including generation-specific VTU/STU data packing, get-next iteration, load/purge, flush, and VTU violation interrupt handling.

Important APIs/types/functions: exports generic and family-specific `*_vtu_getnext()`, `*_vtu_loadpurge()`, `mv88e6xxx_g1_vtu_flush()`, `*_stu_getnext()`, `*_stu_loadpurge()`, and VTU problem IRQ setup/free. Private helpers read/write FID, SID, VID valid/page bits, and 6185/6352 versus 6390 data layouts.

Control flow: VTU/STU operations wait for the busy bit, seed VID or SID only when starting from an invalid entry, issue a get-next/load-purge command, then read or write generation-specific data registers. VTU flush also clears `chip->fid_bitmap`. Violation IRQ handling reads and clears violation status, decodes SPID/VID, traces, and increments per-port counters.

State and persistence: VLAN membership, FID policy, SID mapping, and STP states are hardware table state. `chip->fid_bitmap` is software cache/state refreshed around VTU use.

Dependencies/integration: used by DSA bridge VLAN and STP paths, devlink VTU/STU snapshots, tracepoints, IRQ domains, and Global1 register definitions.

Risks: old and new chips pack membership/state differently; errors can create wrong VLAN membership or spanning-tree forwarding state. VID page handling extends VID encoding beyond 12 bits on some chips. IRQ paths index per-port counters from SPID without broad validation.

Test signals: bridge VLAN add/delete/dump, STP state changes, flush after VLAN teardown, devlink VTU/STU dumps, and synthetic or hardware VTU miss/member violation counters.
