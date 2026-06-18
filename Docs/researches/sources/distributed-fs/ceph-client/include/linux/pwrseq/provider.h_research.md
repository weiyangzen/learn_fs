# sources/distributed-fs/ceph-client/include/linux/pwrseq/provider.h

Purpose: declares the provider-side API and data model for registering reusable power sequencers composed of dependency-ordered units and named targets.

Important APIs and types: callback typedefs are `pwrseq_power_state_func` and `pwrseq_match_func`; match results are `PWRSEQ_NO_MATCH` and `PWRSEQ_MATCH_OK`. `struct pwrseq_unit_data` describes a named unit, its NULL-terminated dependencies, and enable/disable callbacks. `struct pwrseq_target_data` names a target, final required unit, and optional post-enable callback run after the state lock is released. `struct pwrseq_config` supplies parent device, owner, driver data, match callback, and NULL-terminated targets. APIs register/unregister providers, devm-register providers, and retrieve driver data.

Control flow: a provider defines units and dependency graph, defines targets, registers a `pwrseq_device`, and matches consumers by device. The core enables dependencies before a target unit, disables in reverse dependency order, and can run post-enable delays outside the state lock.

State and persistence: provider state includes registered sequencer device, target/unit state, dependencies, module ownership, and driver data. Hardware side effects are runtime power/reset state.

Dependencies and integration points: depends on device model, modules, consumer API, and provider drivers for regulators, GPIOs, clocks, resets, or board-specific sequencing.

Risks and test signals: risks include cyclic or unterminated dependency arrays, post-enable races after lock release, provider removal with active consumers, and incorrect match decisions. Test dependency ordering, shared targets, provider unregister under references, post-enable delays, devm cleanup, and failure rollback when a unit enable fails.
