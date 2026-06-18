## sources/cloud-native/moby/daemon/libnetwork/osl/kernel/knobs_linux.go

Purpose: Linux implementation of applying kernel sysctl tweaks under `/proc/sys`.

Important APIs/types/functions: `writeSystemProperty`, `readSystemProperty`, and `ApplyOSTweaks`.

Control flow: keys such as `net.ipv4.vs.conn_reuse_mode` are converted to `/proc/sys/net/ipv4/vs/conn_reuse_mode`; `ApplyOSTweaks` reads the old value, skips missing keys, logs read errors, checks whether the desired value should apply, writes the new value, and logs either warning or debug output.

State and persistence behavior: mutates live kernel sysctl state. Changes are process-external and may affect host networking/IPVS behavior until changed again or rebooted depending on sysctl persistence outside Docker.

Dependencies and integration points: called by OSL namespace `ApplyOSTweaks` for load-balancer and ingress sandboxes. Uses `os` file IO and containerd logging.

Risks: writes to host `/proc/sys`, requiring privileges and correct kernel module availability. Missing files are silently skipped; write failures are warnings, not fatal. The code writes raw value strings without newline normalization.

Test signals: `knobs_linux_test.go` reads/writes selected neighbor GC thresholds when available and restores old values, providing basic sysctl IO coverage.
