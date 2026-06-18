## sources/cloud-native/moby/integration/config/config_test.go

Purpose: API-level swarm config integration tests. Coverage includes inspect raw JSON fidelity, listing and filters, create/delete errors, label updates, rejection of data updates, templated configs referencing secrets/configs, and ID/name-prefix resolution.

Important functions are `createConfig`, `configNamesFromList`, and tests such as `TestConfigInspect`, `TestConfigList`, `TestConfigsUpdate`, `TestTemplatedConfig`, and `TestConfigCreateResolve`. Control flow starts a swarm via `integration/internal/swarm`, creates configs/secrets through the Go client, lists/inspects/updates/removes them, and for templating creates a service, waits for a running task, execs `cat /templated_config`, and checks tmpfs mount output.

State includes swarm configs, labels, versions, secrets, services, task files, and raw API JSON. Dependencies include client config APIs, errdefs, swarm helpers, `stdcopy`, `poll`, and Windows skips. Risks include swarm convergence timing, config version requirements, templating semantics, and name-vs-ID ambiguity. Test signals are list names, not-found/invalid-argument errors, updated labels, rendered config content, tmpfs mount text, and successful prefix resolution rules.
