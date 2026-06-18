# sources/cloud-native/moby/daemon/graphdriver/driver.go

Purpose: central graphdriver interfaces, registration, selection, and prior-driver detection.

Important APIs and control flow: `CreateOpts`, `InitFunc`, `ProtoDriver`, `DiffDriver`, `Driver`, `DiffGetterDriver`, and `FileGetCloser` define the storage-driver contract. `Register` stores init functions by name and rejects duplicates; `IsRegistered` queries the registry. `New` either initializes an explicitly requested driver after checking removed names, or scans existing non-empty driver directories, picks a prior driver in platform priority order, errors if multiple prior drivers exist, otherwise tries priority drivers and then all registered drivers skipping `ErrUnSupported` errors. `scanPriorDrivers` ignores `vfs`, and `isEmptyDir` treats open/read errors as non-empty. `checkRemoved` rejects removed `aufs`, `devicemapper`, and legacy `overlay`.

State, dependencies, and risks: state is the package-global driver registry and platform `priority`. Persistent detection is based on directories under the graph root. Dependencies include filesystem stat/read, logging, and user ID mappings passed to drivers. Risks include ambiguous prior state blocking daemon startup, map iteration fallback order being nondeterministic, and support errors needing to implement `NotSupported`. Tests cover only `isEmptyDir`.
