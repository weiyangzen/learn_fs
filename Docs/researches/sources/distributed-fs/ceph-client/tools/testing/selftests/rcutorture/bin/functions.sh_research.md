# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/functions.sh

Purpose: shared shell function library for rcutorture scripts, covering argument validation, boot-parameter/config helpers, qemu identification/argument generation, CPU and network qemu options, colored diagnostics, timing, and ftrace extraction.

Important APIs and functions: `checkarg`, `configfrag_boot_params`, `configfrag_boot_cpus`, `configfrag_boot_maxcpus`, `configfrag_hotplug_cpu`, `identify_boot_image`, `identify_qemu`, `identify_qemu_append`, `identify_qemu_args`, `identify_qemu_vcpus`, `specify_qemu_cpus`, `specify_qemu_net`, `print_bug`, `print_warning`, and `extract_ftrace_from_console`.

Control flow: sourced by many scripts; functions are invoked to normalize CLI validation, derive qemu command/image from built kernel architecture, append qemu CPU/net/serial arguments, and parse ftrace sections.

State and persistence: mostly stateless, but uses environment variables such as `TORTURE_QEMU_CMD`, `TORTURE_BOOT_IMAGE`, `TORTURE_QEMU_INTERACTIVE`, and `TORTURE_QEMU_MAC`.

Dependencies and integration: central integration point for `kvm.sh`, `kvm-test-1-run.sh`, recheck scripts, and rerun/remote tooling.

Risks and test signals: architecture detection depends on `file` output and explicit case lists. Argument helper quoting is simple, so callers must avoid whitespace-heavy paths and untrusted strings.
