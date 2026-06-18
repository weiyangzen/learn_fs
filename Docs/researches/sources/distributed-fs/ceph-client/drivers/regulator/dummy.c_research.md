# sources/distributed-fs/ceph-client/drivers/regulator/dummy.c

Purpose: Creates the global dummy regulator used by the regulator framework for systems or tests without a controllable backing regulator.

Important APIs, types, and functions: The global `dummy_regulator_rdev` stores the registered regulator device. `dummy_initdata` marks the dummy regulator always-on. `dummy_desc` describes a voltage regulator named `regulator-dummy` with id `-1` and an empty operation table. `dummy_regulator_probe()` registers the descriptor on a faux device. `regulator_dummy_init()` creates the faux device named `reg-dummy`.

Control flow: Initialization creates a faux device with `dummy_regulator_driver` ops. The faux device probe registers the dummy regulator using devm registration and stores the returned rdev globally. If faux device allocation or regulator registration fails, the code logs errors and leaves the global unset or error-free only on success.

State and persistence: The dummy regulator has no controllable hardware state; its constraints mark it always on. Lifetime is bound to the faux device, and the rdev pointer is global for framework use.

Dependencies and integration points: It depends on faux device infrastructure, regulator provider registration, machine constraints, and the local `dummy.h` declaration. It is intended for regulator core fallback behavior and tests.

Risks and test signals: Test initialization failure handling, that the dummy regulator is always-on, that consumers do not expect voltage operations from the empty ops table, and that framework users correctly distinguish dummy supplies from real optional supplies when needed.
