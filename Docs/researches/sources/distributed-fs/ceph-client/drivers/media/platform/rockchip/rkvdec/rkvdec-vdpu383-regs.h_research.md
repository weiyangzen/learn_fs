# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-vdpu383-regs.h

Purpose: defines the VDPU383 register layout and link-register constants used by RK3576-class H.264/HEVC backends.

Important APIs and types: offset macros for common, codec parameter, common address, codec address, and POC-highbit regions; mode, timeout, link interrupt, link IP-enable, and decode-enable constants; packed structs `vdpu383_regs_common`, `vdpu383_regs_common_addr`, `vdpu383_regs_h26x_addr`, `vdpu383_regs_h26x_params`, and aggregate `vdpu383_regs_h26x`.

Control flow: VDPU383 codec backends populate these structs and copy them to the function register block, then write link registers (`VDPU383_LINK_TIMEOUT_THRESHOLD`, `VDPU383_LINK_IP_ENABLE`, `VDPU383_LINK_DEC_ENABLE`) to launch decode. The core IRQ handler uses link status and interrupt-enable constants.

State and persistence: no state is stored in the header; it describes the transient MMIO programming image. RCB entries include both offset/address and size fields, unlike VDPU381.

Dependencies and integration points: includes Linux types and bit macros. Consumed by VDPU383 H.264/HEVC code and `rkvdec.c` variant IRQ handling.

Risks: the include guard says `_RKVDEC_VDPU838_REGS_H_`, apparently a typo for VDPU383; it still works but can confuse maintenance. Struct comments and offset constants must match hardware exactly. RCB array length is 11 while the current variant table has 10 entries, so additions must keep both sides aligned.

Test signals: compile coverage, hardware decode on RK3576, link interrupt clear/disable behavior, timeout thresholds, and register dump comparison against vendor programming sequences.
