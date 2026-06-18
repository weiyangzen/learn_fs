# sources/compression/zstd/tests/regression/method.h

Purpose: This header declares the compression method plugin interface used by the regression runner. It abstracts state creation, compression execution, and cleanup so `test.c` can iterate all methods uniformly.

Important APIs and types: `method_state_t` is the base state containing the active `data_t`. Derived states must embed it as a member. `method_t` has `name`, `create(data)`, `compress(state, config)`, and `destroy(state)` fields. `method_set_zstdcli()` sets the CLI executable used by CLI-backed methods. `methods` is the NULL-terminated exported method list.

Control flow: There is no executable flow in the header, but the lifecycle is explicit: create one method state for a dataset, call compress repeatedly for configs, then destroy the state.

State and persistence: State ownership is delegated to each method. The base type carries dataset identity only; derived implementations own buffers or other resources.

Dependencies and integration points: Includes `data.h`, `config.h`, and `result.h`, tying each method to a dataset/config pair and a `result_t` outcome. `test.c` is the primary consumer.

Risks and test signals: Because derived states are recovered with a `container_of` pattern in `method.c`, implementations must return a pointer to the embedded base exactly as documented. A destroy mismatch or partial allocation handling bug can leak or crash. Method names must be comma-free because the result table is comma-separated.
