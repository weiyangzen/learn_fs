# Research: sources/cloud-native/moby/daemon/libnetwork/drvregistry/portmappers_test.go

Purpose: tests the simple portmapper registry contract. Important fixture is `fakePortMapper`, which implements `MapPorts` and `UnmapPorts` with no-op success.

Control flow: registration tests cover a successful registration, blank-name rejection, and duplicate-name rejection. Lookup tests register a fake mapper and assert `Get` returns the same value, then check that a missing name returns an error containing `portmapper nonexistent not found`.

State/dependencies: tests rely on the zero-value `PortMappers` map being lazily initialized. Dependencies include `portmapperapi`, context, and `gotest.tools`. The suite validates the main happy/error paths but does not cover nil mapper values, concurrent access, or integration with Linux NAT/routed portmapper registration. Because `PortMappers` has no lock, these tests are single-threaded and do not exercise data-race risks.
