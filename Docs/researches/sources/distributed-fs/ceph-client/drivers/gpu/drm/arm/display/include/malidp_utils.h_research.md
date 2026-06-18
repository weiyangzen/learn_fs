# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/include/malidp_utils.h

Purpose: supplies common bit/range/polling helpers for Mali display drivers.

Important APIs/types/functions: `has_bit()`, `has_bits()`, `dp_wait_cond()`, `struct malidp_range`, `set_range()`, and `malidp_in_range()`.

Control flow: `dp_wait_cond()` repeatedly sleeps with `usleep_range()` until a condition becomes true or the retry count reaches zero, returning `0` or `-ETIMEDOUT`. Range helpers are used during resource enumeration and atomic validation to check layer/scaler/compositor dimensions.

State and persistence: no persistent state. `dp_wait_cond()` evaluates its condition more than once, so callers must pass expressions safe for repeated evaluation.

Dependencies/integration: includes Linux delay and errno headers. Used by D71 reset/opmode/TBU connect waits and Komeda validation paths.

Risks: macro condition evaluation can hide side effects. `has_bits(bits, mask)` assumes `bits` is the required set and `mask` is the available set; reversed arguments would invert semantics. Poll timing is fixed by callers and may be fragile on slow hardware. Test signals: timeout-path tests for reset/opmode/IOMMU, boundary-value tests for `malidp_range`, and review of all `has_bits()` call sites for argument order.
