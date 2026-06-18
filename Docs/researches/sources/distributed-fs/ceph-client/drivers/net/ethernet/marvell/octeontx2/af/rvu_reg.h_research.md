# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rvu_reg.h

## Purpose

`rvu_reg.h` is the RVU Admin Function register map for OcteonTX2/CN10K/CN20K networking blocks. It gives symbolic offsets and offset-generating macros for RVU AF/PF/VF mailboxes, NPA, NIX, SSO/SSOW, TIM, CPT, NPC, NDC, LBK, and APR register spaces. It is included by AF and NIC-side code that needs to read or program hardware through `rvu_read64()`, `rvu_write64()`, `otx2_read64()`, and mailbox-driven register configuration.

## Important APIs, Types, And Functions

- RVU AF/PF/VF mailbox and interrupt offsets: `RVU_AF_AFPFX_MBOXX()`, `RVU_PF_VFX_PFVF_MBOXX()`, `RVU_PF_PFAF_MBOXX()`, FLR/ME/GEN/MBX interrupt status and enable registers.
- Privileged function mapping registers: `RVU_PRIV_PFX_*`, `RVU_PRIV_HWVFX_*`, and block type revision discovery macros.
- NPA AF and LF configuration offsets for LF reset, admin queues, aura/pool allocation, qints, RAS, poison, and error paths.
- NIX AF offsets for LF allocation, RX/TX queue contexts, scheduler hierarchy, stats, RSS, LSO, VLAN, IPsec, multicast, mirror, timestamp, and backpressure programming.
- CPT offsets for engine, LF, fault, RAS, context cache, inline IPsec, BAR2 alias, and LF queue programming.
- NPC offsets for parser/KPU, key-extract configuration, MCAM, exact-match, debug, and match-stat registers.
- Dynamic NPC MCAM macros such as `NPC_AF_MCAMEX_BANKX_CAMX_W0()` switch register layout when `rvu->hw->npc_ext_set` is set.
- LBK and APR masks define loopback channel/link configuration and LMTST throttle/map fields used by AF/NIC code.

## Control Flow

The header has no runtime control flow, but it shapes most register-level control flow in the AF driver. Callers calculate offsets with these macros, then issue MMIO reads/writes or encode offsets into mailbox register-write requests. Most simple macros are pure arithmetic over block, LF, entry, bank, queue, scheduler, or channel indexes. The NPC MCAM and match-stat macros are GNU statement expressions that inspect the caller-visible `rvu` pointer to choose legacy versus extended NPC address layouts.

## State And Persistence

The file stores no state. Its constants identify volatile hardware state: mailbox doorbells, interrupt enables, LF contexts, NPA pools/auras, NIX queues, scheduler registers, NPC MCAM entries, CPT LF queues, and context caches. Incorrect values persist indirectly by programming hardware into the wrong state until reset or explicit reconfiguration.

## Dependencies And Integration Points

The macros depend on Linux bit helpers such as `BIT_ULL()` and `GENMASK_ULL()` from included users. `rvu_switch.c`, `rvu_rep.c`, AF mailbox handlers, NPA/NIX/CPT/NPC code, and NIC files such as `otx2_common.c`, `cn10k_ipsec.c`, and `cn20k.c` use these offsets. The register map must remain aligned with `rvu_struct.h` context layouts and mailbox ABI structures in `mbox.h`/`npc.h`.

## Risks

- A wrong offset or mask can corrupt unrelated hardware state because all consumers perform raw MMIO or AF-mediated writes.
- The NPC extended-set macros rely on an in-scope variable named `rvu`; they are convenient but fragile if reused in a different naming context.
- Some macros use uncast shifts while others explicitly cast to `u64`; high index values require careful review for overflow and precedence.
- Duplicate names such as `NPC_AF_BLK_RST` appear in adjacent sections and must match the hardware specification.
- New silicon revisions require updating both register offsets and context structures; partial updates are likely to fail only on hardware.

## Test Signals

Validation signals are hardware boot/probe success, mailbox interrupt traffic, resource attach/detach, NPA/NIX AQ operations, MCAM rule programming, CPT/IPsec bring-up, and loopback switch operation. Static review should compare every offset and mask against the hardware reference manual, especially NPC extended-set branches and CN20K mailbox register definitions.
