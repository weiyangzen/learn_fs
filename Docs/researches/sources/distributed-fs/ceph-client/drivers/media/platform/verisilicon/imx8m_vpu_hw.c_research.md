# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/imx8m_vpu_hw.c

## Purpose
`imx8m_vpu_hw.c` describes the NXP i.MX8M Hantro VPU hardware variants. It provides SoC control-register reset/clock helpers, supported G1/G2 format tables, codec operation tables, IRQ/clock/register resource names, shared-device matching, and exported `hantro_variant` definitions for i.MX8MQ and i.MX8MM VPU instances.

## Important APIs, Types, And Functions
Low-level helpers are `imx8m_soft_reset`, `imx8m_clk_enable`, `imx8mq_runtime_resume`, `imx8mq_vpu_hw_init`, and `imx8m_vpu_g1_reset`. Format tables include `imx8m_vpu_dec_fmts`, `imx8m_vpu_postproc_fmts`, `imx8m_vpu_g2_dec_fmts`, and `imx8m_vpu_g2_postproc_fmts`. Codec op arrays map Hantro modes to G1/G2 run/init/exit/reset/done functions. Exported variants are `imx8mq_vpu_variant`, `imx8mq_vpu_g1_variant`, `imx8mq_vpu_g2_variant`, and `imx8mm_vpu_g1_variant`.

## Control Flow
For the combined i.MX8MQ variant, hardware init records the control register base as the last mapped register range. Runtime resume enables all clocks, soft-resets G1 and G2, enables both block clocks in the control register, writes fuse registers to expose decoder/postprocessor capabilities, then disables clocks again. During V4L2 context setup, the core uses the selected variant's format tables and codec ops; stream start later invokes the run/init/exit callbacks selected by codec mode.

## State And Persistence
Persistent driver configuration is static const variant data. Runtime mutable state is limited to MMIO writes under `vpu->ctrl_base` and clock state during resume/reset. Format and codec capability state is not dynamically discovered; it is encoded in these tables.

## Dependencies And Integration Points
The file depends on Linux clock and delay APIs, Hantro core definitions, JPEG/G1/G2 register headers, postprocessor ops, G1 MPEG2/VP8/H264 decode paths, and G2 HEVC/VP9 decode paths. Device-tree compatible matching elsewhere selects these exported variants and resource-name arrays.

## Risks
Resource array ordering matters: the combined variant assumes the control range is the last register base. Fuse register writes are hard-coded to all ones, so changes to control register semantics could advertise unsupported blocks. Split G1/G2 variants use shared device matching, making device-tree binding and clock/resource naming regressions likely if names drift. Format max dimensions and bit-depth/match-depth flags directly affect V4L2 negotiation.

## Test Signals
Probe/runtime-PM tests on i.MX8MQ and i.MX8MM are key. Decode smoke tests should cover MPEG2, VP8, H264 on G1 and HEVC/VP9 on G2, plus postprocessed NV12/YUYV/P010 negotiation where supported. Device-tree resource-name and clock-name validation should accompany binding changes.
