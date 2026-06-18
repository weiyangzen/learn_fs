# sources/distributed-fs/ceph-client/drivers/crypto/cavium/cpt/cpt_hw_types.h

Purpose: describes the Thunder CPT instruction, result, and control/status register bit layouts used by PF and VF code.

Important APIs and types: `enum cpt_comp_e` defines completion codes. `union cpt_inst_s` is the 8-word hardware instruction, `union cpt_res_s` is the 16-byte completion record, and `union cptx_pf_*`/`union cptx_vqx_*` overlays BIST, constants, PF queue control, VF queue base, interrupt, doorbell, done count, coalescing, and enable registers.

Control flow and state: no functions run here; callers fill bitfields before `cpt_write_csr64()` or interpret values after `cpt_read_csr64()` and DMA completion writes. Endian-specific bitfield layouts are guarded by `__BIG_ENDIAN_BITFIELD`.

Dependencies and integration points: consumed by PF initialization, mailbox queue binding, VF queue setup, request submission, and interrupt handlers. It must align with the hardware little-endian instruction/result format unless queue control selects big-endian behavior.

Risks and test signals: risks include C bitfield layout dependency, accidental inclusion cycle with `cpt_common.h`, queue-control changes while inflight, and completion-code polling against stale DMA memory. Test signals include correct BIST and constants decoding, queue doorbell counts in multiples of 8 words, completion records changing from `NOTDONE` to `GOOD/FAULT/SWERR`, and builds on both endian configurations.
