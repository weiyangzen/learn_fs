# subset-b-009400 Research

Work item: `subset-b-009400`

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/common_linux.h -->
# sources/test-tools/syzkaller/executor/common_linux.h

## Purpose

`common_linux.h` is the Linux-specific shared executor/csource support layer for syzkaller. It provides feature-gated helpers used by generated pseudo-syscalls, sandbox entry points, network and device environment setup, repeat-mode cleanup, kernel instrumentation setup, and Linux-only emulation surfaces such as TUN/TAP, raw USB gadget, Bluetooth VHCI, io_uring/ublk, FUSE, BTF, KVM, and filesystem-image mounting.

The file is intentionally conditional. Most blocks are compiled when `SYZ_EXECUTOR` is enabled or when a generated C reproducer references the corresponding `__NR_syz_*` pseudo-syscall or feature macro. That lets the same implementation serve both the full executor and minimized reproducers without pulling every Linux subsystem into every binary.

## Important APIs, Types, And Functions

Core synchronization and utilities:

- `event_t`, `event_init`, `event_reset`, `event_set`, `event_wait`, `event_isset`, and `event_timedwait` implement a tiny futex-backed event primitive for threaded executor operation.
- `write_file()` formats and writes small control values into procfs/sysfs/debugfs files. It is used throughout feature setup and sandbox initialization.
- `runcmdline()` runs shell commands for the few setup paths that use existing tools, notably NIC VF setup and swap setup.

Netlink and networking:

- `struct nlmsg`, `netlink_init`, `netlink_attr`, `netlink_nest`, `netlink_done`, `netlink_send_ext`, `netlink_send`, and `netlink_query_family_id` form the local netlink message builder/sender used by route, generic-netlink, devlink, wireguard, nl80211, and nl802154 setup.
- Link construction helpers include `netlink_add_device`, `netlink_add_veth`, `netlink_add_xfrm`, `netlink_add_hsr`, `netlink_add_linked`, `netlink_add_vlan`, `netlink_add_macvlan`, `netlink_add_geneve`, `netlink_add_ipvlan`, `netlink_device_change`, `netlink_add_addr4`, `netlink_add_addr6`, and `netlink_add_neigh`.
- `initialize_tun()` repairs `/dev/net/tun`, creates `syz_tun`, assigns stable fd `200`, configures static IPv4/IPv6 addresses, permanent neighbors, and a fixed MAC.
- `read_tun()`, `flush_tun()`, `syz_emit_ethernet()`, and `syz_extract_tcp_res()` implement network injection and TCP sequence/ack extraction.
- `initialize_netdevices()` creates a rich test topology in the sandbox namespace: bridges, veth pairs, bonds, teams, hsr, xfrm, virt_wifi, vlan, macvlan, ipvlan, macvtap, macsec, geneve, netdevsim, wireguard, and several existing tunnel devices.
- `initialize_netdevices_init()` configures init-namespace-only devices such as NETROM/ROSE and discovers VF passthrough devices through `find_vf_interface()`.
- `netlink_wireguard_setup()` configures three wireguard peers with deterministic keys, ports, endpoints, and allowed IP halves.
- `initialize_devlink_pci()` moves a devlink PCI instance into the executor namespace and renames devlink ports.
- Wi-Fi support uses `hwsim80211_create_device`, `initialize_wifi_devices`, `nl80211_set_interface`, `nl80211_join_ibss`, `nl80211_setup_ibss_interface`, `await_ifla_operstate`, `syz_80211_inject_frame`, and `syz_80211_join_ibss`.
- IEEE 802.15.4 setup is in `setup_802154()`.

Pseudo-syscall shims and device emulation:

- USB pseudo-syscalls are included through `common_usb_linux.h` when USB support is needed.
- `syz_usbip_server_init()` creates a UNIX socket pair, allocates a per-proc VHCI port, writes the attach request to `/sys/devices/platform/vhci_hcd.0/attach`, and returns the server side.
- `initialize_vhci()`, `process_command_pkt()`, `event_thread()`, and `syz_emit_vhci()` emulate enough Bluetooth HCI/VHCI state to make Bluetooth socket descriptions reachable.
- `syz_open_dev()`, `syz_open_procfs()`, `syz_open_pts()`, `syz_init_net_socket()`, `syz_socket_connect_nvme_tcp()`, `syz_genetlink_get_family_id()`, `syz_memcpy_off()`, `syz_create_resource()`, `syz_pidfd_open()`, `syz_pkey_set()`, and `syz_kfuzztest_run()` are Linux pseudo-syscall helpers exposed to generated programs.
- `syz_clone()` and `syz_clone3()` clear `CLONE_VM`, set clone-in-progress state when segv handling is compiled in, and make child processes sleep briefly before plain `exit`.

Storage, filesystem, and kernel service helpers:

- `setup_loop_device()`, `reset_loop_device()`, `syz_read_part_table()`, and `syz_mount_image()` decompress syzkaller compressed images into memfd-backed loop devices, trigger partition scanning, mount filesystems, and normalize dangerous mount options.
- KVM setup is delegated to architecture headers such as `common_kvm_amd64.h`, `common_kvm_arm64.h`, `common_kvm_ppc64.h`, and related files.
- `read_btf_vmlinux()` and `syz_btf_id_by_name()` parse `/sys/kernel/btf/vmlinux` directly to resolve BTF type IDs by name.
- io_uring and ublk support defines local copies of ring offsets, CQE/SQE structures, ublk control/queue structures, and helpers `syz_io_uring_setup`, `syz_io_uring_submit`, `syz_io_uring_complete`, `syz_io_uring_modify_offsets`, `syz_ublk_setup_io_uring`, `syz_ublk_add_dev`, `syz_ublk_setup_queues`, and `syz_ublk_process_io`.
- FUSE support defines FUSE opcodes and headers, `struct syz_fuse_req_out`, `fuse_send_response()`, and `syz_fuse_handle_req()` for selecting fuzzer-supplied responses per request opcode.

Sandbox and repeat-mode APIs:

- `sandbox_common()` applies parent-death signaling, saves the initial network namespace fd, sets resource limits, unshares namespaces, makes mounts private, and writes IPC sysctls.
- `sandbox_common_mount_tmpfs()` builds a tmpfs-backed chroot/newroot tree, bind-mounts selected system paths, mounts proc/sys/debug/smack/binfmt/syz-inputs as appropriate, initializes cgroup bind mounts, pivots/chroots, and sets up gadgetfs, binderfs, and fusectl.
- `do_sandbox_none()`, `do_sandbox_setuid()`, `do_sandbox_namespace()`, and `do_sandbox_android()` sequence environment setup, capabilities, network namespaces, device initialization, and privilege dropping for each sandbox mode.
- `drop_caps()` removes selected capabilities, primarily `CAP_SYS_PTRACE` and `CAP_SYS_NICE`.
- Android-specific helpers `getcon`, `setcon`, and `setfilecon` manipulate SELinux state without libselinux and `do_sandbox_android()` optionally switches between untrusted app and system credentials.
- `remove_dir()` recursively unmounts and deletes tmp directories while handling busy mounts, immutable flags, and read-only filesystem cases.
- Repeat-mode hooks include `setup_loop()`, `reset_loop()`, `setup_test()`, `close_fds()`, and `kill_and_wait()`.

Feature setup and diagnostics:

- `setup_cgroups`, `mount_cgroups`, `mount_cgroups2`, `setup_cgroups_loop`, `setup_cgroups_test`, and `initialize_cgroups` prepare v1/v2 cgroups and per-test cgroup symlinks.
- `checkpoint_net_namespace()` and `reset_net_namespace()` snapshot and restore iptables, ip6tables, arptables, and ebtables state through locally defined userspace ABI structures.
- `setup_fault()` and `inject_fault()` configure kernel fault-injection files; `fault_injected()` checks and resets fail-nth state.
- `setup_leak()` and `check_leaks()` drive kmemleak with delayed rescans to reduce false positives.
- Other setup functions include `setup_binfmt_misc()`, `setup_kcsan()`, `setup_usb()`, `setup_sysctl()`, and `setup_swap()`.

## Control Flow

The file is not a single control path; it is a library of feature setup routines and pseudo-syscall implementations. The broad executor boot flow compiles into the sandbox entry selected by flags:

1. A sandbox entry (`do_sandbox_none`, `do_sandbox_setuid`, `do_sandbox_namespace`, or `do_sandbox_android`) forks/clones where needed and establishes parent/child ownership through `wait_for_loop()`.
2. It initializes privileged early devices such as VHCI, calls `sandbox_common()`, and optionally drops capabilities or switches credentials.
3. It sets up the initial namespace artifacts: cgroups, init-net devices, a new network namespace, ping group sysctl, devlink PCI, TUN/TAP, virtual network devices, Wi-Fi hwsim, tmpfs/chroot/binder/fuse/gadget mounts.
4. It enters the generated executor `loop()`.

Repeat-mode control flow wraps each program execution:

1. `setup_loop()` may create per-proc cgroups and checkpoint netfilter tables.
2. `setup_test()` sets parent-death behavior, process group, cgroup symlinks, OOM score, TUN drain, and binderfs symlink.
3. The generated program runs pseudo-syscalls and real syscalls.
4. `reset_loop()` clears per-proc loop devices and restores netfilter tables.
5. `close_fds()` closes generated fds including USB emulation fds so coverage can flush and event loops can exit.
6. `kill_and_wait()` escalates stuck test processes and aborts FUSE connections when ordinary SIGKILL waiting is insufficient.

Pseudo-syscalls are generally short wrappers around Linux ABI surfaces. Some have multi-step protocols: USB raw-gadget connection loops over EP0 control events until configuration completes; io_uring setup maps shared rings and exposes pointers to syzlang; ublk setup submits io_uring commands and maps queue buffers; FUSE handling reads a request and dispatches by opcode to a fuzzer-provided response header.

## State And Persistence Behavior

Persistent process globals include:

- `tunfd`, fixed at fd `200` after setup.
- `kInitNetNsFd`, fixed at fd `201` for initial net namespace access.
- `vhci_fd`, fixed at fd `202` after VHCI setup.
- `nlmsg` and `nlmsg2`, shared stack-like netlink buffers.
- Netfilter checkpoint arrays `ipv4_tables`, `ipv6_tables`, `arpt_tables`, and `ebt_tables`.
- `vf_intf`, used to carry VF passthrough discovery into setup.
- `port_alloc[2]` in `syz_usbip_server_init()`, static per process for USB/IP port allocation.
- The static BTF vmlinux cache in `read_btf_vmlinux()`.

Kernel and filesystem state is intentionally mutated. The file writes sysctls, creates network devices and neighbors, mounts cgroups and tmpfs, creates binderfs/gadgetfs/fusectl mounts, configures raw-gadget permissions, enables swap, registers binfmt_misc handlers, changes kmemleak and KCSAN debug knobs, creates loop-device associations, and may attach usbip devices. Some state is per namespace and cleaned by namespace teardown; other state is global or sticky, such as netdevsim devices, sysctls, binfmt_misc entries, swap files, and debugfs knobs.

The cleanup/reset paths are partial but deliberate. Netfilter tables are checkpointed/restored, loop devices are cleared, TUN queues are flushed, cgroups are reused per proc, and tmp directories are aggressively unmounted/deleted. The design accepts that some setup calls can fail on older or differently configured kernels and logs optional failures instead of aborting, while fatal setup dependencies use `fail()` or `failmsg()`.

## Dependencies And Integration Points

This header depends on executor-provided symbols and macros such as `SYZ_EXECUTOR`, `flag_*` feature flags, `procid`, `debug`, `debug_dump_data`, `fail`, `failmsg`, `exitf`, `doexit`, `sleep_ms`, `current_time_ms`, `kMaxThreads`, `kCoverSize`, `syscall_timeout_ms`, `loop()`, and optional `cover_reset`.

It integrates with:

- Linux UAPI headers for netlink, rtnetlink, nl80211, if_tun, if_link, genl, loop, KVM, rfkill, USB, capabilities, sched, cgroups, io_uring-compatible structures, and BTF-compatible copied structs.
- syzkaller headers `common_usb_linux.h`, `common_zlib.h`, architecture-specific `common_kvm_*.h`, and Android seccomp support.
- syzlang descriptions that know fixed names, fds, addresses, handles, and device names, including `syz_tun`, `wlan0/1`, `wg0/1/2`, Bluetooth handles `200/201`, `/dev/loop<procid>`, and many virtual netdevice names.
- Kernel configuration and runtime features such as TUN, netdevsim, wireguard generic netlink, mac80211_hwsim, nl802154, dummy_hcd/raw-gadget, vhci, debugfs, kmemleak, fault injection, cgroup v1/v2, binderfs, fusectl, KCSAN, binfmt_misc, KVM, ublk, io_uring, and USB/IP VHCI.

## Risks And Edge Cases

- Many helper structures mirror Linux UAPI manually. Kernel ABI drift can silently break io_uring, ublk, BTF, netfilter, ebtables, FUSE, USB raw-gadget, and devlink interactions.
- `struct nlmsg` has a fixed 4096-byte buffer and nesting depth 8. The code fails on overflow/bad nesting but large future netlink messages may need explicit resizing.
- Global or sticky host state is modified. netdevsim devices, debugfs knobs, binfmt_misc entries, swap, sysctls, and some device moves can outlive one executor process.
- The setup path intentionally ignores optional failures. That improves portability but can reduce test reachability without making the failure obvious unless debug logs are examined.
- Namespace switching via `setns()` can fail if another thread closes fds; the code treats restoration failure as fatal.
- Several helpers use `sprintf`/fixed buffers with controlled internal strings, but additions should preserve bounds assumptions.
- `read_btf_vmlinux()` caches a fixed 10 MiB BTF blob and has a benign race; larger kernels or short reads at the limit return failure.
- `syz_io_uring_complete()` and `syz_io_uring_submit()` trust ring pointers and do not validate empty/full rings, by design for fuzzing.
- `syz_mount_image()` appends mount options into a 256-byte buffer and only logs when generated options are too large; malformed options are expected in fuzzing but can affect outcome clarity.
- Android sandboxing is architecture-sensitive and relies on direct SELinux xattr/context manipulation.
- `remove_dir()` is intentionally aggressive around mounts and immutable flags; it is risky to reuse outside a disposable executor tmp tree.

## Test Signals

Useful validation signals include:

- Feature-probe failures returned from setup functions, e.g. `setup_fault`, `setup_leak`, `setup_usb`, `setup_swap`, `setup_802154`, `setup_kcsan`, and `setup_binfmt_misc`.
- Debug lines from netlink setup, TUN initialization, wireguard setup, Wi-Fi hwsim setup, devlink port initialization, USB/IP attach, raw-gadget USB, VHCI, io_uring/ublk, FUSE, and mount-image helpers.
- Kernel-visible artifacts: presence of `syz_tun`, virtual netdevices, configured `wlan0/wlan1`, `/syzcgroup/*`, `/dev/binderfs`, `/dev/gadgetfs`, `/sys/fs/fuse/connections`, `/proc/sys/fs/binfmt_misc` registrations, raw-gadget permissions, swap activation, and loop device cleanup.
- Repeat-mode isolation checks: no stale packets after `flush_tun`, netfilter tables restored after `reset_net_namespace`, per-test cgroup symlinks exist, and loop device `LOOP_CLR_FD` succeeds.
- Pseudo-syscall return values: fd-returning helpers return nonnegative fds, generated response helpers return `0`, extraction helpers write expected sequence/ack values, and error paths preserve `errno` where documented.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/common_linux.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/common_openbsd.h -->
# sources/test-tools/syzkaller/executor/common_openbsd.h

## Purpose

`common_openbsd.h` is the OpenBSD-specific shared support layer for syzkaller executor and generated C reproducers. It implements the small set of OpenBSD pseudo-syscalls and sandbox helpers needed to open PTYs, configure tap devices for packet injection, emit/extract Ethernet/TCP traffic, and run tests under either no sandbox or a setuid sandbox.

## Important APIs, Types, And Functions

- `syz_open_pts()` uses `openpty()` to allocate a master/slave pair, duplicates the master fd upward to lower collision risk with fuzzer-generated closes, and returns the slave fd.
- `tunfd` is the process-global fd for the active tap device.
- TUN/TAP constants define per-proc tap names and deterministic local/remote MAC, IPv4, and IPv6 addresses. The OpenBSD implementation supports up to `MAX_TUN` tap instances and derives names such as `/dev/tap%d` and `tap%d`.
- `vsnprintf_check()` and `snprintf_check()` are bounded formatting helpers that fail if generated command strings do not fit their fixed buffers.
- `execute_command()` prepends a fixed PATH and runs `ifconfig`, `arp`, and `ndp` commands via `system()`, optionally treating failure as fatal.
- `initialize_tun(int tun_id)` destroys any old tap instance, opens the requested `/dev/tap%d`, remaps it to fd `200`, configures MAC/IP addresses, and populates ARP/NDP neighbors.
- `syz_emit_ethernet()` writes raw packet data to `tunfd`.
- `read_tun()` reads from `tunfd`, treating `EAGAIN` as no packet.
- `struct tcp_resources` plus `syz_extract_tcp_res()` parse one Ethernet frame and return adjusted TCP sequence and acknowledgement values.
- `sandbox_common()` applies minimal resource limits and, in non-threaded mode, calls `setsid()`.
- `do_sandbox_none()` runs `sandbox_common()`, optional tap initialization, and `loop()`.
- `wait_for_loop()` and `do_sandbox_setuid()` fork a child, initialize tap support, resolve the `nobody` account, drop groups/gid/uid, and run `loop()` in the child.

## Control Flow

The non-sandbox path is direct: `do_sandbox_none()` applies resource limits, initializes tap injection for `procid` when enabled, and enters the generated `loop()`.

The setuid path forks first. The parent waits for the loop child with `waitpid()`, while the child applies `sandbox_common()`, sets up the tap interface while still privileged, switches to the `nobody` user/group with empty supplementary groups, then enters `loop()` and exits through `doexit()` if `loop()` returns.

Network injection control flow is command-driven rather than netlink-driven. `initialize_tun()` formats device/interface names, destroys previous state, opens the tap device, remaps the fd, and executes `ifconfig`, `arp`, and `ndp` commands to prepare layer-2 and layer-3 state. Generated pseudo-syscalls then use `syz_emit_ethernet()` and `syz_extract_tcp_res()` against the global fd.

## State And Persistence Behavior

The main process state is `tunfd`, remapped to fd `200` to keep it above normal generated fd ranges and consistent with syzkaller fd assumptions. The system state is the OpenBSD tap interface and static ARP/NDP entries. `initialize_tun()` tries to destroy a prior tap interface before opening and configuring the new one, but there is no comprehensive reset routine in this header.

Resource limits are process-local: memlock, file size, stack, core, and nofile are capped in `sandbox_common()`. The setuid sandbox persists the dropped credentials for the test child only.

## Dependencies And Integration Points

The file relies on common executor symbols such as `procid`, `loop()`, `debug`, `debug_dump_data`, `fail`, `failmsg`, `doexit`, and compile-time feature macros. It uses OpenBSD libc and system headers including `openpty`, `ifconfig`-visible tap devices, `arp`, `ndp`, `<netinet/ip.h>`, `<netinet/ip6.h>`, `<netinet/tcp.h>`, and `<netinet/if_ether.h>`.

The generated syzlang side must know the same tap fd behavior, address patterns, and TCP resource structure layout. Unlike the Linux version, OpenBSD setup delegates interface configuration to userland tools through `system()` with an explicit PATH.

## Risks And Edge Cases

- `execute_command()` uses a 128-byte command payload after the PATH prefix. New longer commands must either increase `COMMAND_MAX_LEN` or risk fatal formatting failure.
- The tap interface id must be in `[0, MAX_TUN)`, so `procid` mapping must remain bounded by the caller.
- `initialize_tun()` only returns gracefully for missing tap devices in csource mode; executor mode treats open failure as fatal.
- IPv6 parsing in `syz_extract_tcp_res()` does not skip extension headers.
- The Ethernet type branch treats every non-IPv4 frame as IPv6-shaped and then rejects if lengths/protocol do not match.
- Static ARP/NDP entries and tap interfaces may remain if the process exits before cleanup.
- `do_sandbox_setuid()` assumes a `nobody` passwd entry exists.

## Test Signals

- Successful tap setup is visible through `ifconfig tapN`, static IPv4/IPv6 addresses, and ARP/NDP entries.
- `syz_emit_ethernet()` should return the number of bytes written when `tunfd` is valid.
- `syz_extract_tcp_res()` should return `0` and write network-order adjusted `seq`/`ack` for valid IPv4/IPv6 TCP frames, and `-1` for no packet, malformed Ethernet/IP/TCP headers, or unsupported protocols.
- Sandbox behavior is indicated by child exit status in setuid mode and by expected `RLIMIT_*` values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/common_openbsd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/common_test.h -->
# sources/test-tools/syzkaller/executor/common_test.h

## Purpose

`common_test.h` is the executor/csource support layer for syzkaller's synthetic test OS target. It implements deterministic pseudo-syscalls used by executor tests and fuzzer tests rather than real kernel-environment setup. The file focuses on simple memory mapping, errno shaping, comparisons, controlled crashes, coverage injection hooks, and no-op feature setup.

## Important APIs, Types, And Functions

- `syz_mmap()` maps a fixed anonymous private writable mapping at a requested address and length.
- `syz_errno()` sets `errno` to the provided value and returns `0` for zero or `-1` otherwise.
- `syz_exit()` exits through the executor-provided `doexit()`.
- `syz_sleep_ms()` delegates to the common `sleep_ms()` helper.
- `syz_compare()` checks byte-for-byte equality between expected and actual buffers, sets `EBADF` on length mismatch and `EINVAL` on content mismatch, and dumps both buffers on error.
- `syz_compare_int()` accepts a count from 2 to 4 and compares a vararg set of integer values while checking unused arguments are zero.
- `syz_compare_zlib()` decompresses a generated zlib image into `./uncompressed`, mmaps the result if non-empty, and compares it through `syz_compare()`.
- `do_sandbox_none()` rejects unsupported net injection and devlink PCI feature combinations for the test OS, then enters `loop()`.
- `fake_crash()` and `syz_test_fuzzer1()` produce named synthetic crashes for specific argument triples.
- `syz_inject_cover()` and `syz_inject_remote_cover()` are declarations in executor builds, with csource stubs returning `0`.
- `setup_sysctl()` and `setup_cgroups()` are no-op placeholders.

## Control Flow

Most pseudo-syscalls return immediately after performing one deterministic action. Comparison helpers branch to a shared error path that logs buffer contents before returning `-1`.

`do_sandbox_none()` is the only sandbox entry. It deliberately fails if net injection is requested and exits with a feature message if devlink PCI is requested. Otherwise it calls the generated `loop()` directly.

`syz_test_fuzzer1()` implements two reproducible crash triggers: `(1, 1, 1)` and `(1, 2, 3)`. Both call `fake_crash()`, which emits a `failmsg()` formatted with `{{CRASH: ...}}` and exits.

## State And Persistence Behavior

The file has almost no durable state. `syz_errno()` intentionally mutates thread/process `errno`; `syz_compare_zlib()` creates `./uncompressed` with `O_EXCL` and leaves normal file lifetime to the surrounding executor/test cleanup; `syz_mmap()` mutates the process address space. Coverage injection hooks may affect executor coverage state when linked with `executor_test.h`, but the csource stubs do not.

## Dependencies And Integration Points

The file uses common executor facilities such as `doexit`, `sleep_ms`, `debug`, `debug_dump_data`, `fail`, `failmsg`, `exitf`, feature flags, and `loop()`. zlib comparison depends on `common_zlib.h` and `puff_zlib_to_file()`.

The synthetic crash strings are intended for syzkaller report detection and fuzzer tests. `syz_inject_cover` and `syz_inject_remote_cover` are resolved by executor test-specific code in executor builds.

## Risks And Edge Cases

- `syz_compare_zlib()` returns `-1` without closing/unmapping on several error paths; this is acceptable in short-lived tests but should not be used as a long-running library pattern.
- `syz_compare_int()` reads four varargs regardless of `n`; callers must pass the full generated signature.
- `syz_mmap()` uses `MAP_FIXED`, so it can replace existing mappings in the test process.
- `syz_compare()` dumps arbitrary input buffers on mismatch, which is useful for tests but can produce large logs if lengths are large.
- `do_sandbox_none()` intentionally rejects features rather than trying to emulate them, so feature-detection tests should expect failure messages.

## Test Signals

- Unit-style generated programs can assert return values and `errno` from `syz_errno`, `syz_compare`, and `syz_compare_int`.
- Synthetic crash detection should classify the two `syz_test_fuzzer1()` argument triples as distinct named crashes.
- Coverage tests should link executor definitions for `syz_inject_cover` and `syz_inject_remote_cover`; csource mode should see harmless `0` returns.
- zlib comparison tests can check that decompressed bytes match and mismatches set the expected comparison errors.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/common_test.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/common_usb.h -->
# sources/test-tools/syzkaller/executor/common_usb.h

## Purpose

`common_usb.h` contains the generic, OS-independent portions of syzkaller's virtual USB pseudo-syscall implementation. It parses generated USB descriptors into compact indexes, tracks descriptor metadata by emulated device fd, provides optional debug analysis for USB classes and control requests, and implements request-to-response lookup for USB connect and control I/O helpers. Linux-specific raw-gadget transport code lives in `common_usb_linux.h`.

## Important APIs, Types, And Functions

Descriptor indexes:

- `USB_MAX_IFACE_NUM`, `USB_MAX_EP_NUM`, and `USB_MAX_FDS` bound indexed interfaces, endpoints, and active device fds.
- `struct usb_endpoint_index` stores a copied endpoint descriptor and a Linux raw-gadget endpoint handle.
- `struct usb_iface_index` stores a pointer to the original interface descriptor, cached interface number/alternate/class, an endpoint array, and endpoint count.
- `struct usb_device_index` stores device/config descriptor pointers, cached device class/max power, config length, interface indexes, interface count, and current interface index.
- `struct usb_info` binds an fd to a `usb_device_index`.
- `usb_devices[]` and `usb_devices_num` hold process-local active USB device metadata.
- `lookup_usb_index()` finds metadata by fd using atomic fd loads.
- `parse_usb_descriptor()` walks a descriptor buffer, records up to four interfaces and 32 endpoints per interface, and caches selected descriptor fields.
- `add_usb_index()` atomically allocates a table slot, parses descriptors, and publishes the fd with release ordering.

Debug analysis:

- `usb_class_to_string()` maps common USB class IDs to readable names.
- `analyze_usb_device()` logs vendor/product, device class, and interface classes.
- `analyze_control_request_standard()`, `analyze_control_request_class()`, `analyze_control_request_vendor()`, and `analyze_control_request()` classify setup packets and mark whether a request has known response semantics. Unknown IN requests can emit a diagnostic to `/dev/kmsg`.

Connect descriptors and response lookup:

- `struct vusb_connect_string_descriptor` and `struct vusb_connect_descriptors` describe optional qualifier, BOS, and string descriptor responses generated by syzlang.
- `default_string` and `default_lang_id` provide fallback UTF-16 "syz" and language ID string descriptors.
- `lookup_connect_response_in()` resolves standard GET_DESCRIPTOR responses for device, config, string, BOS, and device qualifier requests. It can synthesize a device qualifier from the device descriptor.
- `lookup_connect_out_response_t` is the function-pointer type for connect OUT request handlers.
- `lookup_connect_response_out_generic()` treats SET_CONFIGURATION as the terminal request for generic USB connect.
- `lookup_connect_response_out_ath9k()` handles ath9k firmware download vendor requests and terminates on `ATH9K_FIRMWARE_DOWNLOAD_COMP`.

Control I/O descriptors:

- `struct vusb_descriptor`, `struct vusb_descriptors`, `struct vusb_response`, and `struct vusb_responses` describe generated response tables for `syz_usb_control_io`.
- `lookup_control_response()` searches exact descriptor/response entries first and falls back to generic descriptor or response payloads.

## Control Flow

Connection setup first calls `add_usb_index()`, which parses the raw generated device and configuration descriptor blob. The transport-specific connect loop in `common_usb_linux.h` then uses `lookup_connect_response_in()` for IN control requests and a selected OUT handler for OUT requests. Generic connection ends on SET_CONFIGURATION; ath9k-specific connection continues through firmware download commands.

Descriptor parsing is a single forward pass over the provided buffer. The parser stops on short descriptors, length overrun, or descriptor length <= 2. Interface descriptors create new interface slots until the maximum is reached; endpoint descriptors attach to the most recently seen interface.

For control I/O after connection, Linux code fetches one raw-gadget control event and asks `lookup_control_response()` for fuzzer-provided data. GET_DESCRIPTOR requests match by request type and descriptor type; other requests match by request type and request number.

## State And Persistence Behavior

The persistent state is `usb_devices[]`, which stores pointers into the original generated descriptor buffer. The code does not deep-copy the device and config descriptor bodies, only selected endpoint descriptors. Therefore the generated descriptor memory must remain valid while the fd is used.

`add_usb_index()` increments `usb_devices_num` before parsing. If parsing fails or the table is full, the counter is not rolled back. That is acceptable for short-lived executor runs but means failed connect attempts consume table capacity. The fd is published only after a successful parse, so `lookup_usb_index()` will not match failed slots.

The current active interface (`iface_cur`) and endpoint handles are later mutated by Linux raw-gadget code in `set_interface()`.

## Dependencies And Integration Points

This generic header expects USB descriptor types and request constants from Linux USB headers or equivalent includes, plus executor helpers such as `debug`, `debug_dump_data`, `write_file`, and feature macros. `USB_DEBUG` pulls in Linux USB class headers for richer diagnostics, so debug mode is more Linux-tied than the descriptor-indexing core.

`common_usb_linux.h` consumes `lookup_usb_index`, `add_usb_index`, `lookup_connect_response_in`, the OUT response callbacks, and `lookup_control_response`. syzlang definitions must match the packed descriptor table layouts used here.

## Risks And Edge Cases

- Descriptor pointers refer to caller-provided memory. If a generated program frees, remaps, or mutates that memory while the fd remains active, later request handling observes the changed data.
- The parser trusts that endpoint descriptors have at least `sizeof(struct usb_endpoint_descriptor)` bytes once descriptor length fits the total buffer; malformed short endpoint descriptors could still be copied as a full endpoint descriptor from the buffer region.
- `USB_MAX_FDS` is small and failed `add_usb_index()` attempts still advance `usb_devices_num`.
- `lookup_connect_response_in()` dereferences `descs` for BOS and qualifier responses without checking it in every branch; callers should provide a valid descriptors object for those request types.
- Debug analysis assumes `iface_cur` is valid when reading `index->ifaces[index->iface_cur]`; if called before interface selection, malformed state can make diagnostics unsafe.
- Unknown IN requests in debug mode write to `/dev/kmsg`, which is useful for triage but can add host-visible noise.

## Test Signals

- Parsing tests should confirm interface and endpoint counts, cached class values, config length, and `iface_cur == -1`.
- Connection tests can issue GET_DESCRIPTOR for device, config, string zero, arbitrary string, BOS, and qualifier requests and verify selected fallback or generated responses.
- Ath9k connect tests should verify the terminal OUT request is firmware download completion rather than SET_CONFIGURATION.
- Control I/O tests should cover exact descriptor matches, exact request matches, generic fallback entries, zero-length responses, and missing-response failure.
- Concurrency-sensitive tests can check that `lookup_usb_index()` only observes fds after successful parse/publish.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/common_usb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/common_usb_linux.h -->
# sources/test-tools/syzkaller/executor/common_usb_linux.h

## Purpose

`common_usb_linux.h` is the Linux raw-gadget transport implementation for syzkaller USB pseudo-syscalls. It wraps `/dev/raw-gadget` ioctls, connects generated virtual USB devices to dummy UDC instances, services endpoint-zero control requests, enables/disables raw endpoints for the current interface, and exposes endpoint read/write/control/disconnect pseudo-syscalls.

## Important APIs, Types, And Functions

Raw-gadget ABI definitions:

- `struct usb_raw_init`, `enum usb_raw_event_type`, `struct usb_raw_event`, `struct usb_raw_ep_io`, `struct usb_raw_ep_caps`, `struct usb_raw_ep_limits`, `struct usb_raw_ep_info`, and `struct usb_raw_eps_info` locally mirror the raw-gadget userspace ABI.
- `USB_RAW_IOCTL_*` macros define init, run, event fetch, EP0 read/write/stall, endpoint enable/disable/read/write, configure, vbus draw, and endpoint information ioctls.
- Thin wrappers include `usb_raw_open`, `usb_raw_init`, `usb_raw_run`, `usb_raw_configure`, `usb_raw_vbus_draw`, `usb_raw_ep0_write`, `usb_raw_ep0_read`, `usb_raw_event_fetch`, `usb_raw_ep_enable`, `usb_raw_ep_disable`, `usb_raw_ep0_stall`, `usb_raw_ep_write`, and `usb_raw_ep_read`.

Lookup and state helpers:

- `lookup_interface()` finds a parsed interface by interface number and alternate setting.
- `lookup_endpoint()` finds the raw-gadget handle for an endpoint address on the current interface.
- `USB_MAX_PACKET_SIZE` caps EP0 and endpoint transfer buffers at 4096 bytes.
- `struct usb_raw_control_event` and `struct usb_raw_ep_io_data` are fixed-size stack containers for raw events and I/O payloads.
- `set_interface()` disables endpoints from the previous interface, enables endpoints for the requested interface, stores returned endpoint handles into `usb_endpoint_index.handle`, and updates `iface_cur`.
- `configure_device()` draws configured bus power, issues raw-gadget configure, and activates interface 0.

Pseudo-syscalls:

- `syz_usb_connect_impl()` implements the shared connection loop for generic and ath9k USB connect.
- `syz_usb_connect()` passes the generic OUT request handler from `common_usb.h`.
- `syz_usb_connect_ath9k()` passes the ath9k-specific OUT request handler.
- `syz_usb_control_io()` handles one later EP0 control request using fuzzer-provided descriptor/response tables.
- `syz_usb_ep_write()` writes fuzzer data to a non-control endpoint by endpoint address.
- `syz_usb_ep_read()` reads from a non-control endpoint into fuzzer-provided memory.
- `syz_usb_disconnect()` closes the raw-gadget fd and sleeps briefly.

## Control Flow

`syz_usb_connect_impl()` is the central flow:

1. Validate and debug-dump the generated descriptor blob.
2. Open `/dev/raw-gadget`; reject fds above `MAX_FDS`.
3. Parse and publish descriptor indexes through `add_usb_index()`.
4. Initialize raw-gadget with speed, driver `"dummy_udc"`, and device name `dummy_udc.<procid>`.
5. Run the gadget.
6. Loop fetching raw-gadget events until the OUT handler marks connection done.
7. Ignore non-control events.
8. For IN control requests, resolve data through `lookup_connect_response_in()` or stall EP0.
9. For OUT control requests, call the selected OUT handler, optionally configure the device on SET_CONFIGURATION, then read the host payload.
10. Clamp response length to both the local 4096-byte buffer and `wLength`, perform EP0 read/write, and return the fd after a short sleep.

`syz_usb_control_io()` handles a single post-connect control event. It stalls unknown IN requests, handles SET_INTERFACE-like requests by switching active endpoint sets, fills or consumes EP0 data, and sleeps briefly before returning.

Endpoint read/write pseudo-syscalls translate a USB endpoint address to the raw endpoint handle cached by `set_interface()`, clamp length to 4096 bytes, perform the raw-gadget endpoint ioctl, and sleep.

## State And Persistence Behavior

This file mutates the generic USB index state from `common_usb.h`. `set_interface()` writes endpoint handles into the selected interface's endpoint indexes and updates `iface_cur`; `lookup_endpoint()` depends on that current-interface state.

The raw-gadget fd is returned to the generated program and also used as the key for `lookup_usb_index()`. Closing it via `syz_usb_disconnect()` does not remove the corresponding `usb_devices[]` slot. Because fd numbers may be reused, stale metadata can be a risk if a later raw-gadget connection reuses a closed fd while the table also contains older entries; lookup returns the first matching published fd.

The code introduces short `sleep_ms(200)` delays after connect/config/control/endpoint operations to let kernel-side USB state settle and to improve reproducibility.

## Dependencies And Integration Points

The implementation includes `common_usb.h` and depends on its descriptor parsing and response lookup functions. It expects Linux raw-gadget support at `/dev/raw-gadget`, dummy UDC devices named `dummy_udc.<procid>`, USB descriptor/request constants, `MAX_FDS` from the Linux executor header, and common executor symbols such as `procid`, `debug`, `debug_dump_data`, `sleep_ms`, and feature macros.

It is tightly coupled to syzlang layouts for `vusb_connect_descriptors`, `vusb_descriptors`, `vusb_responses`, endpoint pseudo-syscall signatures, and raw USB descriptor blobs.

## Risks And Edge Cases

- The raw-gadget ABI structs and ioctl numbers are copied locally. Kernel ABI changes require updating this header.
- `usb_raw_init()` uses `strncpy()` into fixed-size arrays without forcing a trailing NUL if input strings are too long. Current call sites use short constants.
- `syz_usb_connect_impl()` leaks the raw-gadget fd on some early failures after open/add/init/run errors because it returns without closing.
- `add_usb_index()` metadata remains after disconnect and failed cleanup, making fd reuse a possible stale-state hazard.
- EP0 response lengths above 4096 are converted to zero rather than truncated to 4096, while `wLength` is treated as the host-side cap.
- In `syz_usb_control_io()`, the condition for interface switching uses standard request type or `USB_REQ_SET_INTERFACE`; future class/vendor requests with the same request number may trigger interface lookup.
- Endpoint I/O requires a current interface. Before configuration or after failed interface setup, `lookup_endpoint()` returns `-1`.
- OUT request debug dumping in connect logs `event.data`, while the read payload is held in the response buffer; this may not show the actual just-read bytes.

## Test Signals

- Raw-gadget availability is indicated by successful open/init/run against `/dev/raw-gadget` and `dummy_udc.<procid>`.
- Connect tests should see EP0 request logs for GET_DESCRIPTOR, SET_CONFIGURATION, optional ath9k vendor requests, and final configured fd return.
- After SET_CONFIGURATION or SET_INTERFACE, endpoint enable/disable debug lines should show endpoint addresses and raw handles.
- Endpoint tests should verify `syz_usb_ep_write` and `syz_usb_ep_read` return success only for endpoints present in the current interface.
- Control I/O tests should cover unknown IN stall behavior, generated response lookup, OUT payload consumption, and interface switching by number/alternate setting.
- Disconnect should close the fd and allow raw-gadget event loops to unwind in executor close-fd cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/common_usb_linux.h -->
