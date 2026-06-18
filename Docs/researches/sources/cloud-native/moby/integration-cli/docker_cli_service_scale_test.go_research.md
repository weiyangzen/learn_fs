## sources/cloud-native/moby/integration-cli/docker_cli_service_scale_test.go

Purpose: checks `docker service scale` accepts valid replicated-service scaling and rejects invalid replica values and global-mode scaling. The single `TestServiceScale` covers a replicated service and a global service.

Control flow creates a swarm daemon, builds platform-specific sleep commands with `sleepCommandForDaemonPlatform`, creates two services, scales `TestService1=2`, and then runs negative cases for `foobar`, `-1`, and `TestService2=2`. State is the swarm service mode and replica count. The file depends on `DockerSwarmSuite`, daemon CLI wrappers, `testutil.GetContext`, and assertion comparators.

Risks are limited but include platform differences in long-running command choice and daemon validation message drift. Integration points are swarm service spec validation and CLI error rendering. Test signals are successful CLI exit for valid scaling and output containing the service name plus either `invalid replicas value` or `scale can only be used with replicated or replicated-job mode`.
