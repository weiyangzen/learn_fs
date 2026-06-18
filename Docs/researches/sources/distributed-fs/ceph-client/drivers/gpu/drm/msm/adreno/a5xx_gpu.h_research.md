# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a5xx_gpu.h

## Purpose
`a5xx_gpu.h` declares the A5xx generation state, preemption record ABI shared with microcode, power/preemption/debugfs entry points, and small helpers used across A5xx source files.

## Important APIs, Types, And Functions
`struct a5xx_gpu` embeds `adreno_gpu` and stores PM4/PFP/GPMU firmware BOs, LM leakage, current/next ring, per-ring preemption BOs/records/IOVAs/counters, last seqnos, atomic preempt state, preempt lock/timer, rptr shadow BO, and `has_whereami`. `enum preempt_state` defines the software state machine. `struct a5xx_preempt_record` is the microcode-visible record. Exports include `a5xx_gpu_funcs`, `a5xx_power_init`, `a5xx_gpmu_ucode_init`, `a5xx_idle`, `a5xx_set_hwcg`, `a5xx_preempt_*`, and `a5xx_flush`.

## Control Flow
The header has no executable control flow except inline helpers. `spin_usecs` polls a register for a masked value with microsecond delays, `shadowptr` computes per-ring rptr shadow IOVA, and `a5xx_in_preempt` reports whether the atomic state is outside normal/abort.

## State And Persistence
This header defines most persistent A5xx runtime state. Preemption records are 64 KiB each plus a separate counter block; the CPU fills fields such as `magic`, `cntl`, `wptr`, `rptr_addr`, `rbase`, and `counter`, while CP firmware saves/restores additional hidden record content.

## Dependencies And Integration Points
It includes `adreno_gpu.h` and generated `a5xx.xml.h`. It links `a5xx_gpu.c`, `a5xx_power.c`, `a5xx_preempt.c`, and optionally `a5xx_debugfs.c`. The record format is an ABI with A5xx PM4/PFP microcode.

## Risks
Changing `struct a5xx_preempt_record` layout, record size, or magic breaks CP preemption. Memory barriers around `preempt_state` are required because IRQ and submit paths inspect it concurrently. `shadowptr` assumes a compact per-ring u32 shadow array.

## Test Signals
Compile coverage plus multi-ring preemption tests are primary. Runtime signals include valid preempt record magic, successful `spin_usecs` waits in power paths, correct rptr shadow updates, and clean preempt resource free.
