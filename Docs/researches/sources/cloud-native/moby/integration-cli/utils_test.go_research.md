## sources/cloud-native/moby/integration-cli/utils_test.go

Purpose: general cross-platform helpers for integration CLI tests. It normalizes daemon paths, parses cgroup files, creates random temp paths, runs command pipelines, lists existing Docker objects, and filters pre-existing objects from CLI output.

Important APIs are `getPrefixAndSlashFromDaemonPlatform`, `dPath`, `ParseCgroupPaths`, `RandomTmpDirPath`, `RunCommandPipelineWithOutput`, `existingElements`, `ExistingContainerIDs`, `ExistingContainerNames`, `RemoveLinesForExistingElements`, and `RemoveOutputForExistingElements`.

Control flow is text and process oriented: convert paths by daemon OS, split `/proc/<pid>/cgroup` lines into controller paths, wire stdout pipes between commands, and remove matching lines by substring. State observed includes `testEnv.DaemonInfo`, environment `TEMP`, and current Docker object lists. Dependencies include `cli`, `exec.Cmd`, and `testutil.GenerateRandomAlphaOnlyString`. Risks include substring false positives when filtering output, pipeline wait error handling, and Windows path conversion edge cases. Test signals are helper returns used by many tests to make assertions deterministic.
