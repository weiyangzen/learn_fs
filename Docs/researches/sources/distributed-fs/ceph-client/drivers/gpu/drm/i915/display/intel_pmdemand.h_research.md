# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pmdemand.h

## Purpose
`intel_pmdemand.h` declares the public PM Demand interface used by Intel display initialization, atomic validation, and commit code. It exposes the opaque PM Demand global-state type and the operations needed to initialize, update inputs, and program PM Demand around plane updates.

## Important APIs And Control Flow
`to_intel_pmdemand_state()` converts from `struct intel_global_state` to the PM Demand state container. `intel_pmdemand_init_early()` initializes synchronization primitives, while `intel_pmdemand_init()` allocates and registers the global atomic object.

`intel_pmdemand_atomic_check()` is called during atomic validation. If PM Demand inputs changed, it pulls the global object into the transaction and computes new parameters. `intel_pmdemand_pre_plane_update()` and `intel_pmdemand_post_plane_update()` are commit-phase hooks used before and after plane programming.

`intel_pmdemand_init_pmdemand_params()` reads initial hardware values, `intel_pmdemand_program_dbuf()` programs display-init DBUF count, and the update helpers maintain persistent DDI-clock and non-Type-C PHY inputs.

## State, Dependencies, Risks, And Test Signals
The header intentionally forward-declares most types and includes only `linux/types.h`, so it does not own state directly. Its API contract assumes callers pass a valid `struct intel_display`, `struct intel_atomic_state`, or PM Demand global state obtained through Intel atomic helpers.

The notable interface risk is argument semantics: `intel_pmdemand_update_phys_mask()` takes a boolean named `clear_bit` in the header but implemented as `set_bit` in the C file. The type is identical, so builds succeed, but readers must consult the implementation or call sites to avoid inverted meaning.

Test coverage is provided by building all PM Demand users and running atomic commit paths that call the declared check and pre/post update hooks on supported display versions.
