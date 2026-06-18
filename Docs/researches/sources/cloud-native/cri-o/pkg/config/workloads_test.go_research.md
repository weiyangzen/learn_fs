# sources/cloud-native/cri-o/pkg/config/workloads_test.go

This file tests workload validation and OCI spec mutation from workload annotations. It verifies invalid cpusets, `cpuquota < cpushares`, and `cpuperiod < 1000` are rejected, while individual valid resource defaults pass. It also confirms that `Resources.MutateSpec` writes CPU cpuset, shares, quota, and period to `specs.LinuxResources`.

The annotation mutation tests construct a workload with an activation annotation and a per-container JSON resource annotation. They check `cpulimit` conversion to quota, `cpulimit` precedence over `cpuquota`, direct quota, cpuperiod, and cpushares. State is local test data plus generated OCI specs; there is no filesystem persistence.

Dependencies include Ginkgo/Gomega, OCI runtime spec and generator packages, and CRI-O config. Integration signal is useful for the exact JSON annotation contract and CFS quota conversion. Gaps include no tests for `AllowedAnnotations`, `FilterDisallowedAnnotations`, nil resources/defaults, invalid JSON, multiple simultaneously active workloads, or map iteration ordering.
