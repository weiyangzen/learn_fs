<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/container_sleep.json -->
# sources/cloud-native/cri-o/test/testdata/container_sleep.json

Purpose: simple long-running CRI container fixture for lifecycle tests.

Important structure: metadata `podsandbox-sleep`, Fedora CI image, command `/bin/sleep 6000` and args `6000`, minimal PATH/GLIBC tunable environment, pod annotation, pod PID namespace, writable rootfs, and basic CPU/memory/OOM resource settings.

State and integration: static request body for creating a container that remains available for stop, exec, inspect, and resource tests. Risks include duplicated sleep duration in command and args, image availability, and resource compatibility across cgroup versions. Test signal is lifecycle stability.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/container_sleep.json -->
