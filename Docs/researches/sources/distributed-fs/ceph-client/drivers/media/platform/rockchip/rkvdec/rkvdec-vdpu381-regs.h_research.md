# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-vdpu381-regs.h

Purpose: defines the VDPU381 register map used by RK3588-class H.264 and HEVC decode backends. It splits the hardware register space into common control, codec parameter, common address, codec address, and POC-highbit regions.

Important APIs and types: offset macros such as `OFFSET_COMMON_REGS`, `OFFSET_CODEC_PARAMS_REGS`, `OFFSET_COMMON_ADDR_REGS`, and `OFFSET_CODEC_ADDR_REGS`; mode and interrupt constants; packed structs `rkvdec_vdpu381_regs_common`, `rkvdec_vdpu381_regs_common_addr`, H.264/HEVC parameter structs, H.26x address/high-POC structs, and aggregate `rkvdec_vdpu381_regs_h264`/`hevc`.

Control flow: VDPU381 codec backends fill these structs in memory and write each region with `rkvdec_memcpy_toio`; the core IRQ handler reads `VDPU381_REG_STA_INT` and applies status-bit constants.

State and persistence: the header stores no software state. It is a packed representation of hardware register words and must remain stable across all jobs for the same hardware generation.

Dependencies and integration points: includes Linux types and bit macros through kernel headers. Integrated by `rkvdec-vdpu381-h264.c`, `rkvdec-vdpu381-hevc.c`, and core interrupt/probe logic.

Risks: the include guard name `_RKVDEC_REGS_H_` collides conceptually with the older `rkvdec-regs.h` guard style, though the literal names differ enough in this tree. Bitfield layout, reserved holes, and register offsets are high-risk: a one-word drift would program wrong MMIO. RCB array length is fixed at 10 and must match variant tables.

Test signals: compile-time struct size checks would be valuable, but runtime signals are successful H.264/HEVC decode, known-good MMIO dumps, IRQ status handling, and no accesses outside mapped resources.
