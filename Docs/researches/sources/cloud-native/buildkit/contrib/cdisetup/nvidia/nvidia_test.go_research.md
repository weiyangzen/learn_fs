# Research: sources/cloud-native/buildkit/contrib/cdisetup/nvidia/nvidia_test.go

Purpose: unit-tests NVIDIA driver version parsing for two observed `/proc/driver/nvidia/version` formats.

Important flow: `TestParseVersion` passes classic UNIX kernel module text and newer open kernel module text to `parseVersion`, asserting extracted major.minor strings `550.120` and `550.144`.

State and dependencies: no filesystem or package-manager side effects. It depends on testify assertions.

Risks and test signals: the test protects the regex used to choose matching driver-library package names. It does not test validation, apt repository setup, package installation, WSL detection, PCI scanning, or CDI YAML generation.
