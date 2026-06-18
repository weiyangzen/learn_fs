# sources/control-plane/ceph-csi/internal/rbd/cgroup_qos_test.go

Purpose: Unit tests for cgroup v2 QoS parsing, validation, path construction, ordering, and `io.max` writes.

Important APIs/types/functions: Tests `parseCgroupQoSParams`, `hasCgroupQoSParams`, `cgroupQoS.formatIOMax`, `validateCgroupQoSParams`, `findPodCgroupPath` error cases, cgroup path construction logic, `qosClassInfo` ordering, and `writeIOMax`.

Control flow: Table tests validate full/partial/default QoS values, presence detection, all `io.max` combinations, invalid string/zero/negative values, empty pod UID and missing pod path errors, Kubernetes UID hyphen-to-underscore conversion, expected slice prefixes, and file write content.

State and persistence behavior: Tests use temp files for `io.max` writing but do not write real cgroup paths. They do not use RBD metadata.

Dependencies and integration points: Uses standard testing, temp dirs, filepath, and string utilities. Supports `cgroup_qos.go` assumptions about cgroup path layout and parameter validation.

Risks: Since `findPodCgroupPath` uses the real `/sys/fs/cgroup`, only negative cases are portable. No test covers successful cgroup detection with an injectable base path, nor device ID lookup from `/proc/partitions`.

Test signals: Good parser and formatter coverage. Limited system integration coverage by design.
