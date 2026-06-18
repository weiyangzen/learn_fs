# sources/cloud-native/buildkit/client/info.go

Purpose: public client API for retrieving daemon version information and converting API CDI device structures.

Important APIs/types/functions: `Info` contains `BuildkitVersion`. `BuildkitVersion` stores package, version, revision, and optional Dockerfile frontend version. `CDIDevice` mirrors CDI fields. `Client.Info` calls the control API and maps version data. `fromAPIBuildkitVersion` and `fromAPICDIDevices` convert API types.

Control flow: `Client.Info` issues an empty `InfoRequest`, wraps call errors, and returns an `Info` with nil-safe version conversion. CDI conversion appends each input device to output.

State and persistence: no local persistence; returns daemon state at call time.

Dependencies/integration points: BuildKit control API and API types. CDI conversion is a helper for other client-facing APIs even though `Client.Info` currently returns only version data.

Risks/test signals: nil version becomes zero-value fields. `fromAPICDIDevices` assumes non-nil device entries; nil entries would panic. No direct tests in this subset.
