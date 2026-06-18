# Research: sources/cloud-native/containerd/internal/cri/server/update_runtime_config_test.go

This test file validates the CNI config generation path in `UpdateRuntimeConfig`. It creates a temporary CNI template using `PodCIDR`, `PodCIDRRanges`, and `Routes`, configures a test CRI service with a temporary CNI config directory and template path, and sends a dual-stack pod CIDR string containing IPv4 and IPv6 CIDRs.

The subtests cover four paths: empty CIDR does not generate a file, missing template does not generate a file, already-ready network does not generate a file, and a configured template with an unhealthy/unloadable fake CNI plugin generates `10-containerd-net.conflist`. For generation, it asserts the rendered config uses the first CIDR as `.PodCIDR`, includes both CIDR ranges, and adds both `0.0.0.0/0` and `::/0` routes.

The tests exercise filesystem persistence by writing the template and reading the generated config from a temp directory. They use `servertesting.FakeCNIPlugin` to force `Status` and `Load` errors. Covered risks include accidental config generation when not needed and incorrect route/range rendering. Gaps include invalid CIDR errors, template parse errors, directory creation errors, atomic close errors, nil default CNI plugin behavior, and metric side effects.
