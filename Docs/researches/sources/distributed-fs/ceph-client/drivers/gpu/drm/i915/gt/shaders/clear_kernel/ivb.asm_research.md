# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/shaders/clear_kernel/ivb.asm

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/shaders/clear_kernel/ivb.asm

### Purpose
`ivb.asm` is the Ivy Bridge variant of the PAVP/cache clear EU kernel. It performs the same GRF clearing and 32x16 zero block writes as the HSW version with IVB-appropriate branch distances and state-register assumptions.

### Important APIs, Types, And Functions
The shader consumes the documented curbe dwords, BTI 0 render target, and optional BTI 1 instrumentation buffer. It uses media block read/write messages, state register decoding, delay-loop arithmetic, indirect GRF writes through `a0`, and EOT via the thread spawner.

### Control Flow
It conditionally skips instrumentation, otherwise increments the histogram cell for the running EU/thread, delays for the requested iterations, writes zero blocks through BTI 0, loops over GRFs writing the clear word, then sends EOT.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
The only persistent effect is on the bound surfaces. It depends on IVB/HSW-compatible but generation-sensitive EU assembly encodings and is consumed by i915 shader build/use paths. Risks include stale jump offsets, invalid surface layout assumptions, and register state differences across platforms. Test signals are clean kernel completion, expected render-cache clearing, and instrumentation rows matching executed threads.
