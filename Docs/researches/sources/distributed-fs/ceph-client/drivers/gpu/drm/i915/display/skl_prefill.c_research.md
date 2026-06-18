# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/skl_prefill.c

### Purpose
`skl_prefill.c` computes display pipe prefill requirements in fixed-point scanlines. It combines fixed frame-start and memory-translation costs with watermark, scaler, DSC, and CDCLK adjustment factors to determine whether vblank is long enough, how much VRR guardband is needed, and what minimum CDCLK is required for prefill.

### Important APIs, Types, And Functions
Public functions are `skl_prefill_init_worst()`, `skl_prefill_init()`, `skl_prefill_vblank_too_short()`, `skl_prefill_min_guardband()`, and `skl_prefill_min_cdclk()`. Internal helpers convert microseconds to `.16` scanlines, initialize fixed components, combine no-CDCLK/scaler/CDCLK stages, and apply `.16` adjustment factors.

### Control Flow
Initialization zeros the context, adds frame-start delay and a fixed 20 us translation-walk cost, then adds DSC prefill. The normal path pulls live WM0/scaler prefill and CDCLK adjustment helpers; the worst path pulls maximum/worst versions for guardband planning. Prefill composition applies second-scaler adjustment, second-scaler lines, first-scaler adjustment, first-scaler lines, WM0, then CDCLK adjustment, and finally fixed overhead. Query functions add caller-specified latency, compare against vblank length, round guardband to whole lines, or ask CDCLK code for a frequency that fits the available prefill window.

### State, Persistence, And Dependencies
State is caller-owned `struct skl_prefill_ctx`, holding `.16` line counts and adjustment factors. No hardware state is written here. Dependencies include CDCLK helpers, display modes, vblank length, VDSC prefill, scaler prefill helpers, and watermark prefill helpers.

### Integration Points
VRR optimized guardband uses `skl_prefill_init_worst()` and `skl_prefill_min_guardband()`. CDCLK and watermark calculations can use the normal context to detect too-short vblank or derive minimum CDCLK. DSC and scaler modules contribute prefill components through their exported helpers.

### Risks
All arithmetic is fixed-point `.16`; mixing raw lines and fixed-point values would skew guardbands. `skl_prefill_min_cdclk()` subtracts fixed overhead from vblank-derived availability, so callers must avoid using it when vblank is shorter than fixed cost. Current constants include a hardcoded 20 us translation cost and simplistic scaler/DSC inputs.

### Test Signals
Useful tests compare guardband/min-CDCLK results across modes, CDCLK changes, watermark latency changes, active scalers, DSC on/off, and VRR guardband limits. Boundary tests should cover very short vblank and high-latency SAGV/package-C states.
