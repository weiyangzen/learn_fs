# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_dcb.h

## Purpose
This header defines the public DCB integration surface for qlcnic. It hides optional `CONFIG_QLCNIC_DCB` support behind wrappers, declares the DCB object and operation table, and provides safe inline dispatch helpers used by the rest of the driver.

## Important APIs, Types, And Functions
- `QLCNIC_DCB_STATE` and `QLCNIC_DCB_AEN_MODE` are state-bit indices used by the DCB implementation.
- `qlcnic_register_dcb()` is declared when DCB is enabled and compiled as a no-op returning success when disabled.
- `struct qlcnic_dcb_ops` defines callbacks for hardware capability queries, CEE parameter queries/config, DCBNL operation initialization, AEN handling, attach, free, and info refresh.
- `struct qlcnic_dcb` stores raw parameters, adapter backpointer, delayed AEN work, workqueue, ops table, mapped config, and state bits.
- Inline wrappers include `qlcnic_dcb_get_hw_capability()`, `qlcnic_dcb_free()`, `qlcnic_dcb_attach()`, `qlcnic_dcb_query_hw_capability()`, `qlcnic_dcb_get_info()`, `qlcnic_dcb_query_cee_param()`, `qlcnic_dcb_get_cee_cfg()`, `qlcnic_dcb_aen_handler()`, `qlcnic_dcb_init_dcbnl_ops()`, and `qlcnic_dcb_enable()`.

## Control Flow
Callers allocate/register DCB through `qlcnic_register_dcb()`, enable it through `qlcnic_dcb_enable()`, refresh firmware-derived state with `qlcnic_dcb_get_info()`, expose DCBNL ops through `qlcnic_dcb_init_dcbnl_ops()`, and handle adapter events with `qlcnic_dcb_aen_handler()`. Each wrapper checks both object and callback presence before dispatching.

## State And Persistence Behavior
The header itself stores no state, but it standardizes state access through `struct qlcnic_dcb`. The wrappers return `-EOPNOTSUPP` when a DCB object or callback is unavailable, except `qlcnic_dcb_enable()` which treats a missing DCB object as success so non-DCB or disabled-DCB builds do not fail adapter initialization.

## Dependencies And Integration Points
This header is included by core qlcnic init/reset paths and the DCB implementation. It depends on the driver adapter type and Linux error codes. Its compile-time no-op behavior is the key integration point that lets callers use DCB hooks unconditionally regardless of kernel config.

## Risks And Edge Cases
- Most wrappers dereference `dcb->ops` without checking that `ops` itself is non-NULL when `dcb` exists; registration must assign ops before wrappers are used.
- Missing callbacks map to `-EOPNOTSUPP`, which callers must either tolerate or treat as a real failure depending on context.
- `qlcnic_dcb_enable()` returning success for NULL DCB is intentional but can mask registration failures if callers expect DCB to be mandatory.

## Test Signals
Compile coverage should include both `CONFIG_QLCNIC_DCB=y` and disabled builds. Runtime signals include successful no-op adapter init when DCB is disabled, valid wrapper return values for missing/unsupported callbacks, and correct dispatch to 82xx/83xx ops after registration.
