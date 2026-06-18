## sources/cloud-native/moby/integration-cli/requirements_test.go

Purpose: central requirement-gating helpers for integration CLI tests. Functions report daemon OS, architecture, network availability, AppArmor, snapshotter mode, userns support, pause support, registry hosting, swarm inactivity, and BuildKit mode.

Control flow is mostly predicate evaluation against `testEnv.DaemonInfo`, environment variables, filesystem probes, HTTP GET to Docker Hub, or lightweight Docker/API calls. `testRequires` iterates predicates and skips the test with a derived requirement name when any returns false.

State observed includes daemon info, host `/proc` and `/sys` files, environment variables, registry binary PATH, swarm local node state, and existing networks. Dependencies include Docker client, containerd plugin constants, registry utilities, and Go reflection/runtime to format skip names. Risks are network probe panics on errors, predicates with side effects such as running a container for read-only userns, and requirement names derived from function symbols. Test signals are skip decisions, not pass/fail assertions, but incorrect predicates can hide coverage or run unsupported tests.
