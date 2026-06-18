# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/lib/kconfig.c

Purpose: this file implements runtime feature detection for TCP-AO selftests. Instead of trusting build-time config alone, it probes network namespaces, veth, TCP-AO, TCP-MD5, VRF, and ftrace availability.

Important APIs and functions: `struct kconfig_t` pairs cached error state with a probe function. Probe functions are `has_net_ns`, `has_veth`, `has_tcp_ao`, `has_tcp_md5`, `has_vrfs`, and `has_ftrace`. The public API is `kernel_config_has`, with skip messages exported through `tests_skip_reason`.

Control flow: `kernel_config_has` locks `kconfig_lock`, lazily runs the relevant probe if the cached state is `KCONFIG_UNKNOWN`, converts zero error to true, and unlocks. Probes create sockets, namespaces, veth devices, VRFs, or TCP-AO/MD5 keys as needed, then clean up local descriptors and namespace context.

State and persistence: state is a process-local `kconfig` array caching positive or negative probe results. Some probes temporarily create namespaces or devices through netlink helpers. No durable files are modified, though `has_ftrace` may mount tracefs via `test_setup_tracing`.

Dependencies and integration points: depends on aolib namespace, netlink, AO key, MD5, VRF, and tracing helpers. It is called by tests directly and by `should_skip_test` wrappers in `aolib.h`.

Risks: `has_tcp_md5` has a suspicious condition `errno != ENOPROTOOPT && errno == ENOMEM`, which only logs ENOMEM and may ignore other unexpected errors. Some probes use `test_error` on initialization failures, making feature detection fatal rather than skippable for infrastructure errors. Ftrace probing has side effects because it initializes tracing.

Test signals: missing optional features produce skip messages such as unsupported TCP-MD5, VRF, or ftrace. Missing required features cause tests using `should_skip_test` or setup code to skip or fail early.
