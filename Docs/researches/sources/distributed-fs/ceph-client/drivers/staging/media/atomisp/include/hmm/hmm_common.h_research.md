# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/include/hmm/hmm_common.h

## Purpose
This small header centralizes HMM diagnostic guard macros used by the HMM and BO layers. The macros log to `atomisp_dev` and return or jump when common validation predicates fail.

## Important APIs, Types, And Macros
- `HMM_BO_NAME` names the subsystem as `"HMM"`.
- `var_equal_return()`, `var_equal_return_void()`, and `var_equal_goto()` check equality and log before returning or jumping.
- `var_not_equal_goto()` checks inequality and logs before jumping.
- `check_null_return()` and `check_null_return_void()` specialize the equality macros for null-pointer validation.

## Control Flow
These macros inject early-return and goto-based error paths into callers. They evaluate a condition, emit `dev_err(atomisp_dev, ...)`, and alter control flow with the supplied return expression or label.

## State And Persistence
The header owns no runtime state, but it depends on a visible `atomisp_dev` symbol in the includer/translation unit. Macro side effects include logging and early exit.

## Dependencies And Integration Points
The macros are consumed by `hmm_bo.h` wrappers and likely HMM implementation files. They assume kernel `dev_err()` is available and that `atomisp_dev` points to a valid device for logging.

## Risks
- Macro arguments may be evaluated in ways callers do not expect; avoid passing expressions with side effects.
- The hidden dependency on `atomisp_dev` makes the macros less reusable and can break compilation if included outside AtomISP contexts.
- Goto/return macros can obscure cleanup structure and make lock handling harder to audit.

## Test Signals
Compile coverage is the key signal. Runtime tests should exercise null and invalid-state paths under lockdep/KASAN to ensure early exits do not leak locks or resources and that logging is safe during init/teardown.
