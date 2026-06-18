# sources/distributed-fs/ceph-client/tools/testing/selftests/kexec/config

This config fragment lists IMA and securityfs options relevant to kexec signature-policy tests. It requests `CONFIG_IMA_APPRAISE=y`, `CONFIG_IMA_ARCH_POLICY=y`, and `CONFIG_SECURITYFS=y`.

There is no executable flow. The fragment is consumed by kselftest configuration tooling and lines up with shell tests that inspect IMA appraisal state, architecture policy, and `/sys/kernel/security/ima/policy`.

The fragment does not request `CONFIG_KEXEC`, `CONFIG_KEXEC_FILE`, or signature-force options; scripts still probe and skip or branch based on the running kernel. Validation signals are securityfs availability and IMA policy visibility when configured.
