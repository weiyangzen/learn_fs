## sources/cloud-native/soci-snapshotter/benchmark/soci_utils.go

Purpose: benchmark utilities for launching/stopping a SOCI snapshotter process and creating containerd containers through the SOCI snapshotter.

Important APIs/types/functions: `SociProcess` tracks the launched command, socket address, root, stdout, and stderr files. `StartSoci` starts the binary and waits for the Unix socket. `StopProcess` kills it and unmounts/removes snapshot roots. `SociRPullImageFromRegistry` pulls using snapshotter `soci` and appends SOCI labels. `CreateSociContainer` creates containers with the SOCI snapshotter.

Control flow: `StartSoci` builds an exec command, creates output log files, starts the process, polls for socket creation up to about 15 seconds, and returns process metadata.

State and persistence: writes stdout/stderr logs, creates snapshotter root state, removes socket/root on stop, and force-unmounts snapshot mountpoints.

Dependencies and integration: containerd client APIs, snapshotter labels from `fs/source`, and benchmark framework resolver/container helpers.

Risks and test signals: process kill errors are ignored, polling uses fixed sleeps, and failed socket startup can leak open files/processes. No direct tests here.
