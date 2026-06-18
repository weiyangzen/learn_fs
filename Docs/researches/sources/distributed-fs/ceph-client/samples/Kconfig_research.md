# sources/distributed-fs/ceph-client/samples/Kconfig

Purpose: defines the kernel configuration menu for optional sample code.

Important APIs/types/functions: top-level `menuconfig SAMPLES` gates all sample options. It declares sample configs for auxdisplay, tracing, ftrace, kobjects, kprobes, rpmsg, livepatch, configfs, connector, fanotify, hidraw, Landlock, pidfd, seccomp, timers, TSM measurements, UHID, VFIO mediated devices, binderfs, VFS, MEI, watchdog, watch_queue, coresight, kmemleak, cgroup, check-exec, hung_task, and sources Rust and DAMON sample Kconfigs. It also declares architecture-provided `HAVE_SAMPLE_FTRACE_DIRECT` symbols.

Control flow: Kconfig dependency logic controls which subdirectories and modules are buildable. Many userspace examples require `CC_CAN_LINK` and `HEADERS_INSTALL`; module samples often require `m`.

State and persistence: configuration state is stored in the kernel `.config`; this file has no runtime state.

Dependencies and integration: consumed by Kconfig and paired with `samples/Makefile`, which maps enabled configs to subdirectories. It integrates with tracing, BPF-adjacent samples indirectly, Rust sample Kconfig, and architecture feature symbols.

Risks: stale dependencies produce broken sample builds or hidden options. Samples that touch privileged kernel APIs may require exact kernel capabilities and headers. Defaulting `SAMPLE_KRETPROBES` to `m` when `SAMPLE_KPROBES` is enabled can surprise minimal module builds.

Test signals: `olddefconfig`, menuconfig visibility checks, allmodconfig/sample builds, and per-sample compile tests with headers installed.
