# sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-mmio-v3.c

## Purpose
`vgic-mmio-v3.c` implements the GICv3 distributor and redistributor MMIO register model. It exposes ITS/LPI capability, GICv4.1 direct SGI controls, redistributor allocation, LPI property and pending base programming, invalidation registers, SGI dispatch helpers, and v3 migration uaccess paths.

## Important APIs, Types, And Functions
Generic utility exports include `extract_bytes()`, `update_64bit_reg()`, cacheability/shareability sanitizers, `vgic_has_its()`, `vgic_supports_direct_msis()`, `system_supports_direct_sgis()`, `vgic_supports_direct_sgis()`, and `vgic_lpis_enabled()`. Descriptor tables are `vgic_v3_dist_registers` and `vgic_v3_rd_registers`. Resource and ABI entry points include `vgic_v3_init_dist_iodev()`, `vgic_register_redist_iodev()`, `vgic_unregister_redist_iodev()`, `vgic_v3_set_redist_base()`, `vgic_v3_has_attr_regs()`, `vgic_v3_dist_uaccess()`, `vgic_v3_redist_uaccess()`, and `vgic_v3_line_level_info_uaccess()`.

## Control Flow
Distributor misc access reports CTLR, TYPER, TYPER2, and IIDR based on VM VGIC state. CTLR writes enable/disable the distributor and update `nassgireq`; changing direct SGI mode reconfigures vSGIs through v4 helpers and may request GICv4 reloads. Redistributor CTLR writes enable or disable LPIs with atomic state transitions, flushing pending LPIs and invalidating ITS caches on disable, or loading LPI state on enable.

PROPBASER and PENDBASER writes are 64-bit-update friendly and sanitized for supported cacheability/shareability and RES0 bits; writes are ignored while LPIs are enabled. INVLPIR and INVALLR set a redistributor busy counter, reload LPI configuration via ITS helpers, and clear the busy state. Redistributor registration picks a free slot from configured redistributor regions, initializes a per-VCPU iodev, and registers a 128 KiB MMIO window. SGI dispatch decodes ICC_SGI* affinity fields and queues target VCPU SGIs or broadcasts to all but the source.

## State And Persistence
Persistent state includes distributor enable, implementation revision, `nassgicap`, `nassgireq`, PROPBASER, each VCPU PENDBASER and redistributor CTLR, redistributor region list, per-VCPU redistributor base/index, SPI IROUTER target MPIDR, LPI pending/config tables, and line-level info for migration. Uaccess writes to TYPER2 can enable direct SGI capability before VGIC initialization if the host supports it.

## Dependencies And Integration Points
It integrates with `vgic-mmio.c` for common per-IRQ state, `vgic-its.c` for LPI invalidation and ITS cache invalidation, `vgic-v4.c` for direct SGI/MSI support, KVM MMIO bus registration, KVM MPIDR/VCPU lookup, guest memory helpers, and system register SGI traps.

## Risks
Redistributor region management is sensitive to overlap, ordering, count, and legacy single-region behavior. Atomic CTLR transitions must prevent simultaneous enable/disable races. LPI base registers are guest-memory pointers, so validation and migration ordering matter. Direct SGI capability is split between host capability, userspace opt-in, and guest request bits. Offsets for shared distributor registers deliberately RAZ/WI private IRQ ranges; descriptor ordering must remain bsearch-compatible.

## Test Signals
Cover v3 distributor and redistributor register uaccess, redistributor-region address APIs with overlap/count/index errors, LPI enable/disable and PROPBASER/PENDBASER sanitization, INVLPIR/INVALLR behavior, TYPER/TYPER2/IIDR migration writes, SGI system-register dispatch routing, direct SGI opt-in paths, and line-level info read/write round trips.
