# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun6i-mipi-csi2/sun6i_mipi_csi2_reg.h

Purpose: defines register offsets and bit masks for the A31 MIPI CSI-2 receiver.

Important APIs and constants: covers controller control bits, configuration lane/channel fields, VC/data-type receive routing, packet number/version registers, per-channel interrupt enable/pending bits, current packet header/ECC/checksum/frame/line registers, and channel register stride macro.

Control flow: no executable code. The C file writes control/config/VC-DT and clears interrupt-pending registers; interrupt masks are defined for future or diagnostic use.

State and persistence: hardware register descriptions only.

Dependencies and integration points: relies on `BIT` and `GENMASK` being available through included kernel headers before use. It is consumed by the A31 CSI-2 implementation.

Risks: `SUN6I_MIPI_CSI2_CH_INT_PD_CLEAR` is `0xff`, clearing only low interrupt bits despite higher status bits being defined; this matches current usage but may be incomplete if more interrupt handling is added. Bit-field macros mask inputs rather than validating ranges.

Test signals: hardware stream start and register dump comparison with expected lane count/data type; future interrupt tests if channel interrupts are enabled.
