# sources/cloud-native/containerd/integration/failpoint/cmd/runc-fp/main.go

## Purpose

This Linux executable wraps `runc` and dispatches failpoint profiles selected by OCI annotations. It lets tests inject lifecycle faults while still running real runc with the original arguments.

## Important APIs, Types, And Functions

- `failpointProfileKey` is `oci.runc.failpoint.profile`.
- `invoker` and `invokerInterceptor` define wrapper call signatures.
- `failpointProfiles` registers `issue9103` and `delayExec`.
- `setupLog` redirects logrus JSON output to the `--log` file supplied by containerd/go-runc.
- `defaultRuncInvoker` execs `runc` with original arguments and `Pdeathsig=SIGKILL`.
- `failpointProfileFromOCIAnnotation` reads `config.json` and chooses a profile.

## Control Flow

`main` initializes logging, loads the profile from OCI annotations, and invokes it with `defaultRuncInvoker`. The default invoker delegates to the real `runc` binary with `os.Args[1:]`, so profile code can run before/after or around specific runc commands.

## State And Persistence Behavior

The wrapper reads bundle `config.json` and appends logs to the runc log file. It does not persist profile state itself; profiles may coordinate through FIFOs or process signals.

## Dependencies And Integration Points

It integrates with containerd/go-runc command conventions, OCI spec annotations, logrus JSON logs, and Linux process death signal behavior.

## Risks And Edge Cases

The wrapper requires `--log` and a valid profile annotation; missing either is fatal. It assumes `runc` is available in `PATH`. A profile mismatch prevents container startup.

## Test Signals

Successful failpoint tests prove the wrapper can transparently delegate normal runc behavior while applying selected fault injection.
