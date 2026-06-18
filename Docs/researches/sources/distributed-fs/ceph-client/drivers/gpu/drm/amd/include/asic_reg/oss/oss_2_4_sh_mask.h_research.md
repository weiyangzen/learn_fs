# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/oss_2_4_sh_mask.h

## Purpose
`oss_2_4_sh_mask.h` is the OSS 2.4 register field header. For each register defined by `oss_2_4_d.h`, it declares bit masks and shift values in the generated AMD style: `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT`. These definitions are used by AMDGPU register helpers to compose, update, and decode 32-bit MMIO register values without hard-coded bit arithmetic in driver code.

The field catalog covers IH interrupt ring handling, SEM request/mailbox control, SRBM status/reset/debug/perf/virtualization, SDMA0/SDMA1 engine and queue contexts, and HDP/XDP host-data-path/cache/peer-to-peer controls.

## Important APIs, Types, and Functions
- There are no functions or data types. The interface is a generated set of `#define` macros.
- IH fields include PASID LUT entries, ring enable/size/writeback/overflow bits, base/read/write pointer fields, interrupt enable and MC VMID/high-water/credit controls, level/status bits, perf monitor selectors and counters, DSM match fields, and version value.
- SEM fields define MC request swap/credits, client request urgent/transaction bits for SDMA/UVD/VCE/ACP/CPG/CPC, status FIFO/pending flags, EDC disable, mailbox client routing, side/host mailbox payloads, mailbox enables, and workaround bits.
- SRBM fields define power/read behavior, graphics queue selection (`PIPEID`, `MEID`, `VMID`, `QUEUEID`), status/busy/pending bits, soft reset bits for many blocks, clock-enable delays, debug snapshots, read/firewall error attribution, DSM triggers, perf monitor controls, CAM remap fields, per-domain address windows, GRBM/SRBM indirect selection data, and virtualization reset/enable controls.
- SDMA fields are mirrored for `SDMA0` and `SDMA1`. They include microcode address/data, power/clock, global control, chicken/workaround bits, tiling/hash, status/perf, freeze/quantum, power gating/FSM, EDC/threshold/id/version, and GFX/RLC0/RLC1 ring/IB/context/doorbell/watermark/CSA/preempt registers.
- HDP/XDP fields include host path credits/cache invalidation, nonsurface base/info/size/flags, tiling and address config, memio command/status/data, D2H flush/bar update, P2P mailbox/BAR address and validity, MC/host/side config, FIFO/depth/gating controls, busy/sticky/debug status, and BAR high address nibbles.

## Control Flow
The header has no runtime control flow, but it shapes many driver control paths. Code reads a register, clears a mask, shifts a value by the matching `__SHIFT`, applies the mask, and writes it back. The local AMDGPU code also uses `REG_SET_FIELD(register_value, REGISTER, FIELD, value)`, which expands against these macros. Typical flows include:
- IH init: program ring base/writeback addresses, set `IH_RB_CNTL` size/writeback/overflow fields, enable interrupts in `IH_CNTL`, and clear overflow when detected.
- SDMA init: for each SDMA instance and queue, set ring size, endian/swap behavior, writeback controls, VMID/priv bits, polling addresses, IB base/size, doorbell enables, and finally `RB_ENABLE`.
- Reset and idle paths: inspect `SRBM_STATUS*` and `SDMA*_STATUS*` fields, then toggle `SRBM_SOFT_RESET__SOFT_RESET_*` bits if needed.
- HDP flush/config paths: use HDP/XDP masks to configure cache behavior, flush/invalidate, peer BARs, and clock-gating controls.

## State and Persistence Behavior
The macros do not hold state, but every mask maps to persistent hardware state bits in OSS 2.4 registers. Many fields are control latches (`RB_ENABLE`, soft reset, clock gating, cache invalidate), while others are status or sticky/error fields (`RB_OVERFLOW`, `READ_ERROR`, firewall violation, doorbell captured, sticky W1C). Some fields require write-one-to-clear or clear-after-set sequencing; callers must follow the hardware protocol rather than simply setting masks blindly.

## Dependencies and Integration Points
- Must match `oss_2_4_d.h` register names exactly, minus the `mm` prefix used for addresses.
- Pairs with enum values from `oss_2_4_enum.h` for selector fields such as perf events, GRBM/SRBM block selectors, tiling modes, endian modes, and format/address encodings.
- Consumed by `iceland_ih.c` and `sdma_v2_4.c` directly, and by broader AMDGPU CIK/VI-style paths using equivalent register names and `REG_SET_FIELD`.
- Depends on AMDGPU bitfield helper conventions: the double-underscore naming pattern is not cosmetic, it is how helper macros derive `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT`.

## Risks
- A mask or shift mismatch corrupts neighboring fields. This is especially risky in compound control registers such as `IH_RB_CNTL`, `IH_CNTL`, `SRBM_GFX_CNTL`, `SDMA*_GFX_RB_CNTL`, and `HDP_MISC_CNTL`.
- Some fields have names ending in `MASK_MASK` because the hardware field itself is named `..._MASK`. Generic tooling must not collapse these names or assume it is a typo.
- SDMA0 and SDMA1 definitions are intentionally parallel. Divergence can break only one engine, which may appear as intermittent hangs depending on ring assignment.
- Write-one-to-clear and sticky status fields require exact semantics. Treating all masks as normal read-modify-write controls can lose error status or repeatedly clear important events.
- This generated header is large and easy to partially update; address/header/schema version skew between `_d.h`, `_enum.h`, and `_sh_mask.h` can compile but program invalid hardware fields.

## Test Signals
- Compile AMDGPU paths that include this header and use `REG_SET_FIELD` to catch missing macro pairs.
- Exercise IH and SDMA on OSS 2.4 hardware: interrupts arrive, IH overflow clear works, SDMA fences complete, ring writeback pointers update, and doorbells are accepted.
- Inspect debugfs or register dumps for expected field values after init: `IH_RB_CNTL.RB_ENABLE`, `SDMA*_GFX_RB_CNTL.RB_ENABLE/RB_SIZE`, `SRBM_GFX_CNTL` queue routing, and HDP flush/cache fields.
- Stress tests should include suspend/resume, GPU reset, command submission on both SDMA engines, interrupt storms, and cache-coherency-sensitive CPU/GPU buffer sharing.
