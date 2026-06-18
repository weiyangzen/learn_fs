# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/shaders/clear_kernel/hsw.asm

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/shaders/clear_kernel/hsw.asm

### Purpose
`hsw.asm` is a Haswell EU assembly clear kernel for PAVP buffer/cache clearing. It clears assigned GRFs with a caller-provided word and writes zeroes to a 32x16 render-target block to indirectly clear 512 bytes of render/data cache.

### Important APIs, Types, And Functions
The file is raw GPU assembly, not C. Its contract is the documented curbe layout in `g1`, BTI 0 for the 2D cache-clearing surface, and optional BTI 1 instrumentation storage. It uses state register fields, media block read/write sends, a delay loop, address register `a0`, and thread spawner EOT.

### Control Flow
The kernel stores the clear word, optionally records per-EU/thread instrumentation by deriving slice, half-slice, EU, and thread slot IDs from `sr0`, executes a programmable delay, writes two 16x16 zero media blocks, loops through GRF ranges clearing them, and terminates the thread.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
State exists in EU registers and the render/instrumentation surfaces for one dispatch. It depends on HSW send message descriptors and state-register bit layout; the HSW jump distances differ from IVB. It integrates with i915 PAVP/GSC-style clear-kernel dispatch code and generated shader binaries. Risks include generation-specific instruction encoding, off-by-one jump offsets, instrumentation buffer sizing, and curbe/BTI mismatch. Test signals are successful cache clearing, valid instrumentation counts, no EU hangs, and correct EOT completion.
