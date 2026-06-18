<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/container_redis.json -->
# sources/cloud-native/cri-o/test/testdata/container_redis.json

Purpose: CRI container config fixture for launching Redis from the CI image.

Important structure: metadata `podsandbox1-redis`, Fedora CI image, args `docker-entrypoint.sh redis-server`, working directory `/data`, Redis version/download environment, backend label, and pod annotation. Linux resources include memory/CPU/OOM plus `cpuset_cpus` and `cpuset_mems` fixed to `0`; security context uses pod PID namespace, writable rootfs, and adds `sys_admin`.

State and integration: used by CRI-O tests that verify service containers, ports, resources, or entrypoint behavior. It persists no local state, but Redis writes to container data paths. Risks include requiring CPU and memory node `0`, capability policy, image Redis version drift, and working directory/entrypoint assumptions. Test signal is successful Redis start and runtime behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/container_redis.json -->
