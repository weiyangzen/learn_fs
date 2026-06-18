<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/container_config.json -->
# sources/cloud-native/cri-o/test/testdata/container_config.json

Purpose: baseline CRI `ContainerConfig` fixture for creating a small Fedora CI container.

Important structure: metadata names `container1`, image is `quay.io/crio/fedora-crio-ci:latest`, command is `/bin/ls`, environment includes PATH, TERM, GLIBC tunable disabling rseq, and test directory/file values. Labels and annotations identify test type and ownership. Linux resources set CPU quota/period/shares, OOM score, memory limit, root user, pod PID namespace, SELinux label, and added `setuid`/`setgid` capabilities.

State and integration: consumed by `crictl`/CRI-O integration tests as JSON request input. It stores no state itself. Risks include image availability, resource defaults conflicting with host cgroup mode, and exact JSON field compatibility with CRI API versions. Test signal is successful container create/start and metadata/resource assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/container_config.json -->
