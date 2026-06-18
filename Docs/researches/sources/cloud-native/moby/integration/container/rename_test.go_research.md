# sources/cloud-native/moby/integration/container/rename_test.go

Purpose: Container rename API tests for stopped/running containers, invalid names, name reuse, anonymous-to-named DNS, legacy link metadata, same-name errors, and repeated renames.

Important APIs and flow: Tests use `ContainerRename`, `ContainerInspect`, `ContainerRemove`, `NetworkCreate`, and helper `container.Run`. Link-specific tests validate `HostConfig.Links` and alias lookup paths after renaming. `TestRenameAnonymousContainer` creates a custom network, renames an anonymous container, restarts it to register service discovery, and pings by the new name. Same-name and invalid-name tests assert expected errors without changing the current container identity.

State and dependencies: Creates named containers, custom networks, links, and network DNS state. Windows/remote skips apply where legacy links or local rename-link metadata are unsupported.

Risks and signals: It protects daemon name index consistency, DNS registration, and legacy link references. Failures may cause name leaks, broken service discovery, or corrupted link metadata after rename.
