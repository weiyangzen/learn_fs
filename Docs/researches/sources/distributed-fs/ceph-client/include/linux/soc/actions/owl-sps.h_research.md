# sources/distributed-fs/ceph-client/include/linux/soc/actions/owl-sps.h

Purpose: This tiny Actions Semi Owl SoC header exposes a system power switch helper for changing power-gate state through SPS registers.

Important APIs/types/functions: It declares `owl_sps_set_pg(void __iomem *base, u32 pwr_mask, u32 ack_mask, bool enable)`. The arguments identify the MMIO base, the power-control bit mask, the acknowledgement bit mask, and whether the domain is being enabled or disabled.

Control flow: Callers pass the already mapped SPS base and domain-specific masks. The implementation is expected to write the power gate request and poll or check acknowledgement.

State and persistence: State is entirely hardware PM state in SPS registers. Changes affect power domains and therefore the availability of dependent IP blocks until the next power transition.

Dependencies and integration: Requires MMIO annotations and integer types from common kernel headers. It integrates with Actions Owl power-domain or clock/reset code that owns the SPS register map.

Risks and test signals: Bad masks can power down the wrong block or hang waiting for an ack. Validate by toggling each domain, checking register ack transitions, and boot-testing peripherals that depend on the domain.
