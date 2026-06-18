<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/utils/consts.go -->
# sources/cloud-native/cri-o/utils/consts.go

Purpose: tiny shared constants package fragment.

Important API: exports `PodCgroupName = "pod"`, a common prefix/name used by CRI-O cgroup code when constructing or recognizing pod cgroup names.

State and integration: compile-time constant only, no persistence. Risks are broad ripple effects if changed because cgroup paths and tests may assume this exact token. Test signal is indirect through cgroup-related tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/utils/consts.go -->
