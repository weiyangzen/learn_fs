# sources/cloud-native/moby/daemon/exec_linux_test.go

Purpose: Linux unit test for AppArmor profile selection during exec process setup.

Important APIs and control flow: `TestExecSetPlatformOptAppArmor` captures whether AppArmor is supported, creates a daemon config store, and table-tests default, custom profile, privileged container, and privileged container with custom profile. It runs each case for both regular exec and `exec --privileged`, then calls `execSetPlatformOpt` with a minimal container and `specs.Process`, asserting the resulting `ApparmorProfile`.

State, dependencies, and risks: the test depends on host AppArmor support detection, so expected profile is blank when unsupported. It documents a known behavior/possible bug: custom container profiles take precedence over privileged-container unconfined behavior, and exec privileged does not change AppArmor selection. The test exercises only the AppArmor branch; user lookup, capabilities, and rlimit behavior are not covered.
