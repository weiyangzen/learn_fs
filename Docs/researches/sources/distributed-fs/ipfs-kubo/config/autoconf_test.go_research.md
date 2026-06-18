# Research: sources/distributed-fs/ipfs-kubo/config/autoconf_test.go

Purpose: Unit tests for AutoConf defaults, the `autoconf-on` profile, and default init placeholder values.

Important APIs/types/functions: `TestAutoConfDefaults`, `TestAutoConfProfile`, and `TestInitWithAutoValues`.

Control flow, state, and persistence: Tests construct in-memory configs and call profile/init functions. They do not fetch remote autoconf or write repository state.

Dependencies and integration points: Uses `testify/assert` and `require`. It verifies `InitWithIdentity` and `Profiles["autoconf-on"]` set Bootstrap, DNS, Routing delegated routers, IPNS delegated publishers, and AutoConf enablement consistently.

Risks and test signals: Coverage does not exercise cache client behavior, placeholder expansion, private-network rejection, or disabled-auto validation. It is a strong signal that defaults and profile transforms continue to advertise `"auto"` correctly.
