## sources/cloud-native/buildkit/util/network/cniprovider/cni_linux_test.go

Purpose: Linux-only tests for namespace-aware dialing and resolver behavior.

Important tests: `TestDialContextDoesNotEscapeNetNS` creates an isolated namespace and host loopback listeners, then expects dialing `localhost` from target ns to fail rather than escaping. `TestDialContextDialsInsideNetNS` brings up loopback inside namespace and expects success. `TestLoopbackDNSUsesCallerNetNS` verifies resolver dial to a loopback address uses caller namespace. `TestIsLoopbackHost` covers IPv4/IPv6 loopback and non-loopback host strings.

State/control flow: helper `createTestNetNS` requires root, unshares/mounts netns on a locked goroutine, and cleans up. Tests use timeouts to avoid hanging.

Risks covered: Go resolver/Happy Eyeballs namespace escape, loopback DNS handling. Gaps: CNI setup/removal and sysfs sampling are not directly tested.
