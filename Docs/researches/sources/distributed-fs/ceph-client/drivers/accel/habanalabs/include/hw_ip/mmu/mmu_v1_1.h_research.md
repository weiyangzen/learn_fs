## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/hw_ip/mmu/mmu_v1_1.h

### Purpose
`mmu_v1_1.h` defines the v1.1 HabanaLabs MMU virtual-address hop layout and register offsets.

### Important APIs, Types, And Functions
The HOP0-HOP4 masks and shifts mirror the v1.0 five-hop layout. Register offsets differ: `MMU_ASID`, `MMU_HOP0_PA43_12`, `MMU_HOP0_PA49_44`, and `MMU_BUSY` live at the v1.1 MMU register block.

### Control Flow
No runtime code is present. Driver MMU code selects these constants for v1.1 devices, programs ASID/root registers, and waits for `MMU_BUSY` to clear after configuration.

### State, Persistence, And Dependencies
Persistent state is the configured ASID/root page table in hardware. The header depends on the v1.1 register map and common MMU flag/page definitions.

### Integration Points
It is used by HabanaLabs MMU v1.1 configuration paths and shares page-table format expectations with `mmu_general.h`.

### Risks
The layout similarity to v1.0 can hide register-base mistakes. Using `MMU_ASID_BUSY` from v1.0 on v1.1 or vice versa would poll the wrong hardware location.

### Test Signals
Tests should check ASID programming, HOP0 physical-address splits, busy polling, and mappings across hop boundaries on v1.1 ASICs.
