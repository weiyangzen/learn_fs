## sources/distributed-fs/ceph-client/arch/arm/vfp/vfp.h

### Purpose
Private VFP arithmetic and state header defining unpacked single/double formats, normalization helpers, exception constants, operation descriptors, and hardware state entry points.

### Important APIs, Types, And Functions
Defines `struct vfp_single`, `struct vfp_double`, `struct op`, `VFP_*` type/exception constants, packing/unpacking helpers, 64/128-bit arithmetic helpers, `vfp_estimate_div128to64`, `vfp_estimate_sqrt_significand`, normalise/round prototypes, register access prototypes, and `vfp_save_state`/`vfp_load_state`.

### Control Flow
Most code is inline arithmetic used by `vfpsingle.c` and `vfpdouble.c`: unpack packed IEEE values, classify zeros/denormals/infinities/NaNs, perform jamming shifts and wide arithmetic, then repack after rounding. Assembly-backed prototypes bridge C emulation to hardware VFP registers.

### State, Persistence, And Dependencies
State is passed through unpacked structs and per-thread VFP hard state. It depends on ARM inline assembly constraints, `do_div`, VFP register numbering, and config-dependent `VFP_REG_ZERO`.

### Integration Points
Shared by VFP module, hardware assembly, and both precision emulators. It is central to preserving IEEE-754 semantics when hardware bounces instructions for software completion.

### Risks
Rounding and jamming helpers are precision-critical; off-by-one errors create silent FP miscomputations. Register numbering differs with `CONFIG_VFPv3`, so compare-with-zero paths must match hardware capabilities.

### Test Signals
Run IEEE single/double conformance vectors, denormal/NaN/overflow tests, and build both VFPv2 and VFPv3 configurations.
