# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a2xx_gpu.c

## Purpose
`a2xx_gpu.c` implements the MSM DRM Adreno A2xx backend. It wires the common `msm_gpu`/`adreno_gpu` framework to A200/A220/A225 hardware by programming the legacy GPUMMU, loading PM4/PFP firmware, submitting indirect buffers, handling interrupts, exposing register ranges for dumps, and creating the A2xx-specific VM.

## Important APIs, Types, And Functions
The public integration point is `a2xx_gpu_funcs`, whose `.base` methods provide `hw_init`, `submit`, `irq`, `recover`, `destroy`, `gpu_state_get`, `create_vm`, and `get_rptr`, while `.init` points at `a2xx_gpu_init`. Important private helpers are `a2xx_submit`, `a2xx_me_init`, `a2xx_hw_init`, `a2xx_recover`, `a2xx_idle`, `a2xx_irq`, `a2xx_gpu_state_get`, `a2xx_create_vm`, and `a2xx_get_rptr`. The file also owns the `a200_registers`, `a220_registers`, and `a225_registers` debug register range tables.

## Control Flow
Initialization starts in `a2xx_gpu_init`: allocate `struct a2xx_gpu`, initialize the common Adreno object with one ring, choose the register table by chip revision, and return the embedded `msm_gpu`. Hardware bring-up in `a2xx_hw_init` obtains GPUMMU physical addresses from `a2xx_gpummu_params`, halts the ME, resets RBBM, configures MMU client behavior and virtual address range, writes arbiter/cache/interrupt/GMEM registers, calls `adreno_hw_init`, programs ringbuffer base/control, uploads PM4 and PFP firmware, sets CP queue thresholds, clears ME halt, and runs `a2xx_me_init`. `a2xx_me_init` emits `CP_ME_INIT` into the ring, including protected-mode setup unless legacy firmware forced protection off.

Submit flow walks `submit->cmd[]`, skips IB target buffers, conditionally skips context restore buffers when the ring context sequence is unchanged, emits `CP_INDIRECT_BUFFER_PFD` for real buffers, writes the submit seqno to scratch reg 2, waits for idle, writes `CACHE_FLUSH_TS` to the ring fence address, triggers a CP interrupt, and flushes the ring write pointer. IRQ flow reads `MASTER_INT_SIGNAL`, decodes MH, CP, and RBBM substatus, logs unexpected faults, acknowledges each source, then calls `msm_gpu_retire`.

## State And Persistence
Persistent state is held in `struct a2xx_gpu` (`pm_enabled`, `protection_disabled`) and in the shared `adreno_gpu` and `msm_gpu` fields initialized by the common layer. Firmware version detection can set `protection_disabled`, which changes later ME initialization. The file programs hardware registers rather than maintaining large software caches; fences persist through ring memptrs and scratch register writes. The debug state snapshot adds `REG_A2XX_RBBM_STATUS` to the common Adreno state.

## Dependencies And Integration Points
The file depends on `a2xx_gpu.h`, `a2xx.xml.h`, `msm_gem`, `msm_mmu`, Adreno firmware helpers, ring packet macros, GPUMMU helpers in `a2xx_gpummu.c`, and common DRM/MSM recovery, retire, suspend/resume, state, and VM plumbing. `a2xx_create_vm` is the key integration point with the old GPU-side MMU path, using a 16 MiB base and `0xfff * 64 KiB` range.

## Risks
Bring-up is register-order sensitive; ME halt/reset, firmware upload, MMU invalidation, and protected-mode setup must remain in the required order. Legacy firmware disables protection support and changes error coverage. `a2xx_submit` uses 32-bit IB addresses and A2xx packet forms, so it depends on the VM aperture and ring setup matching those constraints. IRQ handling mostly logs non-RB CP errors, so fault diagnosis depends on preserving status before acknowledgements.

## Test Signals
Useful signals are successful probe for A200/A220/A225, PM4/PFP firmware load messages with expected versions, `a2xx_me_init` reaching idle, command submission completing via `CACHE_FLUSH_TS` fence updates, MH/RBBM faults logging and clearing, `create_vm` producing a GPUMMU-backed GPU VM, recovery reinitializing after soft reset, and debug dumps showing A2xx register tables without invalid access faults.
