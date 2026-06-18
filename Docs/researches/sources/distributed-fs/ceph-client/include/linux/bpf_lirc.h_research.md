# sources/distributed-fs/ceph-client/include/linux/bpf_lirc.h

Purpose: Declares BPF attach management for LIRC mode2 infrared programs. It isolates optional LIRC BPF support behind `CONFIG_BPF_LIRC_MODE2`.

Important APIs/types/functions: With the config enabled, `lirc_prog_attach()`, `lirc_prog_detach()`, and `lirc_prog_query()` implement syscall-facing attach, detach, and query operations using `union bpf_attr` and `struct bpf_prog`. With the config disabled, inline stubs return `-EINVAL`.

Control flow: BPF syscall paths route LIRC attach-type operations to these functions. Attach installs a BPF program on a LIRC device/hook, detach removes it, and query reports attached program IDs/counts.

State/persistence: Attachment state is maintained in the LIRC subsystem implementation, not in this header. Program refs should persist while attached and drop on detach/device teardown.

Dependencies/integration: Depends on UAPI BPF definitions, LIRC mode2 driver support, and BPF program lifetime rules.

Risks/test signals: Risks include invalid attr validation, device lifetime races, incorrect stub errno expectations, and program ref leaks. Test signals include BPF LIRC selftests or IR-device tests, attach/query/detach cycles, device unplug while attached, and config builds with `CONFIG_BPF_LIRC_MODE2` both enabled and disabled.
