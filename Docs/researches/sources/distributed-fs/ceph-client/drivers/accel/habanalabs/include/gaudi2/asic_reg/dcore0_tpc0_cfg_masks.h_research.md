# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_cfg_masks.h

Purpose: generated bit-field mask and shift definitions for `DCORE0_TPC0_CFG` TPC registers. It exports 165 value masks plus matching shift macros over the TPC CFG register set.

Important APIs/types/functions: macro-only API. It defines field access metadata for TPC count/id, stall-on-error, clock gates, input-queue rate limiting, TSB MTRR, lock values, CGU disable controls, FP16/FP8 rounding and bias controls, dcache/scoreboard flags, arbitration weights, LUT base addresses, status bits, command/execute/stall fields, interrupt cause/mask fields, opcode execution, thread IDs, and occupancy/credit counters. Important downstream masks include status fields consumed by `gaudi2_masks.h` to form `TPC_IDLE_MASK`.

Control flow: none. External code combines these `_SHIFT` and `_MASK` macros with register values read from addresses in `dcore0_tpc0_cfg_regs.h`.

State and persistence behavior: this header does not store state, but describes the bit layout of persistent hardware state in the TPC CFG block. Correct use determines how software reads status, enables/disables subunits, masks interrupts, and programs execution controls without clobbering unrelated bits.

Dependencies and integration points: included through `gaudi2_regs.h`; directly referenced by `gaudi2_masks.h` for idle/status aggregation. It must match the addresses in `dcore0_tpc0_cfg_regs.h` and functional submaps such as kernel/tensor/QM configuration headers.

Risks: field masks are more fragile than raw register addresses because incorrect bit positions can produce valid-looking writes with wrong side effects. Clock-gate, CGU, interrupt, and protection-related fields can affect availability, fault reporting, and isolation. Callers must apply masks before writes and preserve reserved bits according to hardware rules.

Test signals: static checks that every mask/shift pair is internally consistent; generated diff checks against hardware XML/RTL register specs; runtime tests for TPC idle detection, interrupt masking, rate-limit controls, and status polling; warnings from compile if expected mask names disappear from `gaudi2_masks.h`.
