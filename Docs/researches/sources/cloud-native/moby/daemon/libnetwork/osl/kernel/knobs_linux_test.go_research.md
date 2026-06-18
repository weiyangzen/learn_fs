## sources/cloud-native/moby/daemon/libnetwork/osl/kernel/knobs_linux_test.go

Purpose: Linux test for reading and writing kernel sysctl knob files.

Important APIs/types/functions: `TestReadWriteKnobs` exercises `readSystemProperty` and `writeSystemProperty` for IPv4 neighbor GC threshold sysctls.

Control flow: for each configured key, the test tries to read the current value, skips unavailable paths with a warning, writes `10000`, reads back and asserts equality, then restores the original value.

State and persistence behavior: mutates host kernel sysctls during the test and attempts restoration. If restoration fails, the host setting may be left changed.

Dependencies and integration points: uses containerd logging and gotest assertions. It requires a Linux environment with writable `/proc/sys/net/ipv4/neigh/default/*`.

Risks: privileged and environment-sensitive. It tests raw IO helpers rather than `ApplyOSTweaks` conditional behavior. Running in constrained CI may skip paths or fail writes.

Test signals: basic end-to-end confirmation that sysctl path translation, trimming, writing, and restoration work on available kernels.
