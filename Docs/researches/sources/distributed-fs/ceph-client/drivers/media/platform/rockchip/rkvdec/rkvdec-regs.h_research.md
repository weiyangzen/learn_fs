# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-regs.h

Purpose: describes the original/single-register-region RKVDEC register layout used mainly by legacy HEVC/H.264 code and the VP9 backend. It also defines interrupt, cache, QoS, and decode-mode constants.

Important APIs and types: key constants include `RKVDEC_REG_INTERRUPT`, interrupt/status bits, `RKVDEC_REG_QOS_CTRL`, cache command offsets, and mode values for HEVC/H.264/VP9. Packed register structs include `rkvdec_common_regs`, `rkvdec_h26x_regs`, `rkvdec_vp9_regs`, and top-level `rkvdec_regs`; `struct ref_base` encodes reference surface flags and address fields.

Control flow: codec implementations build an in-memory `struct rkvdec_regs`, fill common and codec-specific fields from V4L2 stateless controls and buffer DMA addresses, then copy the image to MMIO. IRQ handling in `rkvdec.c` reads/writes the interrupt register using the same bit definitions.

State and persistence: no runtime state is stored here; the file is a memory/register contract. Packed bitfields represent volatile hardware configuration and status, so layout correctness is critical.

Dependencies and integration points: depends on Linux `types.h` and bit macros. It integrates with `rkvdec-vp9.c`, legacy H.264/HEVC common backends outside this subset, and core interrupt/watchdog code.

Risks: C bitfield order and packing are compiler/architecture sensitive, though this driver targets Linux kernel build assumptions. Register structs must stay synchronized with hardware manuals. Address bitfields such as 28-bit bases assume alignment and truncation rules that callers must respect.

Test signals: allmodconfig/build coverage, VP9 decode conformance, IRQ status handling, cache command writes, and MMIO traces comparing programmed register words against known-good hardware programming.
