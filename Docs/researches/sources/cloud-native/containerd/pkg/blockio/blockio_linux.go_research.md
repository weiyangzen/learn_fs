<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/blockio/blockio_linux.go -->
# sources/cloud-native/containerd/pkg/blockio/blockio_linux.go

Purpose: Linux integration wrapper around Intel goresctrl block I/O classes for containerd.

Important APIs and functions: `IsEnabled`, `SetConfig`, `ClassNameToLinuxOCI`, and `ContainerClassFromAnnotations`. Package globals include `config` and `configMu`.

Control flow and state: `SetConfig` parses a blockio config file via goresctrl, logs class names, and stores it under a mutex. `IsEnabled` checks whether config is non-nil. `ClassNameToLinuxOCI` translates a class to OCI `LinuxBlockIO`; `ContainerClassFromAnnotations` chooses class name from container/pod annotations using goresctrl rules.

Dependencies and integration: depends on `github.com/intel/goresctrl/pkg/blockio`, OCI runtime spec types, and containerd logging. It feeds runtime spec blockio settings.

Risks and test signals: global mutable config affects all callers and needs synchronization. Config parsing and annotation policy are delegated to goresctrl; failures should surface early during daemon config load.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/blockio/blockio_linux.go -->
