# subset-b-006893 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/vfio_pci_device_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/vfio_pci_device_test.c

## Purpose

`vfio_pci_device_test.c` is a kselftest harness for basic VFIO PCI device access. It opens a user-selected PCI BDF through the local `libvfio` selftest helpers, verifies config-space access, BAR mmap discovery, MSI/MSI-X eventfd wiring, and optional device reset support.

## Important APIs, Types, and Functions

The file uses `FIXTURE()` and `TEST_F()` from `kselftest_harness.h`. `struct iommu`, `struct vfio_pci_device`, and `struct vfio_pci_bar` come from `libvfio.h`. Important helper calls are `vfio_selftests_get_bdf()`, `iommu_init()`, `vfio_pci_device_init()`, `vfio_pci_device_cleanup()`, `vfio_pci_device_match()`, `vfio_pci_config_readw()`, `vfio_pci_config_writew()`, `vfio_pci_irq_enable()`, `vfio_pci_irq_trigger()`, `vfio_pci_irq_disable()`, and `vfio_pci_device_reset()`. The local `read_pci_id_from_sysfs()` macro reads `vendor` and `device` from `/sys/bus/pci/devices/<bdf>/`.

## Control Flow

The main fixture initializes an IOMMU container/group and opens the VFIO PCI device for each test. `config_space_read_write` compares VFIO config space against sysfs vendor/device IDs, toggles `PCI_COMMAND_MASTER`, and confirms the write takes effect. `validate_bars` walks the six standard BARs and checks that mmap-capable regions were automatically mapped by `vfio_pci_device_init()`. A second parameterized fixture runs the same IRQ test for MSI and MSI-X: it limits vector count to `MAX_TEST_MSI`, enables vectors, verifies each eventfd is empty, triggers the vector through VFIO, reads the eventfd value, then disables IRQs. `reset` skips devices without `VFIO_DEVICE_FLAGS_RESET` and calls reset otherwise.

## State and Persistence Behavior

No repository or filesystem state is persisted beyond temporary VFIO file descriptors and sysfs reads. The tests intentionally mutate device state: they toggle PCI bus mastering, enable/disable MSI or MSI-X vectors, and may reset the device. Fixture teardown closes VFIO state and IOMMU mappings.

## Dependencies and Integration Points

The test requires a VFIO-bound PCI device passed by BDF, suitable IOMMU support, `/dev/vfio` access, sysfs PCI attributes, Linux VFIO UAPI definitions, and the selftests `libvfio` helper library. It integrates with the kselftest harness for reporting and skip behavior.

## Risks and Edge Cases

The config-space test assumes bus mastering is initially disabled and that toggling it is safe for the selected device. The IRQ test only validates software trigger/eventfd behavior, not real device-generated interrupts. `ASSERT_GT(open(...), 0)` treats fd 0 as failure even though it is technically valid. Hardware reset and bus-master changes can disturb a device that is not dedicated to testing.

## Test Signals

Expected pass signals are matching sysfs/VFIO IDs, successful bus-master bit transitions, non-null mmap pointers for mmap-capable BARs, `EAGAIN` on empty nonblocking eventfds, eventfd value `1` after each trigger, and a successful reset or skip when reset is unsupported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/vfio_pci_device_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/vfio_pci_driver_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/vfio_pci_driver_test.c

## Purpose

`vfio_pci_driver_test.c` exercises optional selftest driver operations exposed through a VFIO PCI test device. It validates driver init/remove idempotence, DMA memcpy through mapped IOVA ranges, behavior with unmapped IOVA addresses, MSI generation, and sustained DMA copy workloads across all configured IOMMU modes.

## Important APIs, Types, and Functions

The fixture uses `struct iommu`, `struct vfio_pci_device`, `struct vfio_pci_driver`, `struct iova_allocator`, and `struct dma_region` from `libvfio.h`. `region_setup()` mmaps anonymous memory, allocates IOVA space, and calls `iommu_map()`. `region_teardown()` unmaps from the IOMMU and munmaps host memory. Driver interactions include `vfio_pci_driver_init()`, `vfio_pci_driver_remove()`, `vfio_pci_driver_memcpy()`, `vfio_pci_driver_memcpy_start()`, `vfio_pci_driver_memcpy_wait()`, and `vfio_pci_driver_send_msi()`. `ASSERT_NO_MSI()` checks that an eventfd remains empty with `EAGAIN`.

## Control Flow

Fixture setup selects the requested IOMMU mode, opens the VFIO PCI device, initializes an IOVA allocator, maps a 1 GiB memcpy region plus the driver's own 2 MiB region, reserves one unmapped IOVA, initializes the driver, and records the driver's MSI eventfd. The memcpy size is bounded by both the device maximum and half the mapped region so source and destination do not overlap. Individual tests repeatedly remove/reinitialize the driver, perform successful DMA copies, try reads or writes using an unmapped IOVA without requiring a specific device error, generate an MSI and read eventfd value `1`, mix successful DMA, failed/unmapped DMA, and MSI generation, and run a 60-second-bounded storm of up to 250 GiB total copy work.

## State and Persistence Behavior

State is per test instance: VFIO device fd state, IOMMU mappings, anonymous memory buffers, allocated IOVA ranges, eventfds, and the selftest driver's device-visible region. No persistent files are written. The test mutates the selected PCI device through driver init/remove, DMA commands, and MSI generation.

## Dependencies and Integration Points

The test requires a BDF whose VFIO PCI selftest driver ops are present; `device_has_selftests_driver()` skips the suite if not. It depends on VFIO, the chosen IOMMU backend modes, eventfd, anonymous mmap, and the shared selftest `libvfio` helpers.

## Risks and Edge Cases

Mapping a 1 GiB anonymous region can fail under constrained memory or address-space limits. The unmapped-IOVA tests intentionally ignore the command return because not all devices surface IOMMU faults the same way; this means they mainly assert no spurious MSI. The storm test divides by `self->size`, so helper/device setup must never report zero `max_memcpy_size`. Hardware DMA and MSI behavior depend on a real VFIO test device.

## Test Signals

Pass signals include stable init/remove loops, byte-for-byte equality after DMA copy, empty MSI eventfd after memcpy and unmapped IOVA attempts, eventfd value `1` after explicit MSI send, repeated mix-and-match success, and `vfio_pci_driver_memcpy_wait()` returning zero after the large transfer batch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/vfio_pci_driver_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vsock/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vsock/Makefile

## Purpose

This Makefile wires the vsock VM selftest wrapper into kselftest. It builds the shared `tools/testing/vsock/vsock_test` binary and installs it into the selftest output directory, while registering `vmtest.sh` as the test program.

## Important APIs, Types, and Functions

Key variables are `TOOLSDIR`, `VSOCK_TEST_DIR`, `VSOCK_TEST_SRCS`, `TEST_PROGS`, and `TEST_GEN_FILES`. The Makefile delegates `$(MAKE) -C $(VSOCK_TEST_DIR) vsock_test` and uses `install -m 755` to copy the generated binary to `$(OUTPUT)/vsock_test`. It includes `../lib.mk` for the kselftest build contract.

## Control Flow

`make` sees `TEST_PROGS += vmtest.sh` and `TEST_GEN_FILES := vsock_test`. The output binary target depends on the upstream vsock test binary, which in turn depends on all C and header files under `tools/testing/vsock`. Building this selftest therefore rebuilds the generic vsock test before the VM harness runs.

## State and Persistence Behavior

The file writes only build artifacts under `$(OUTPUT)` and the delegated vsock build directory. It has no runtime persistence.

## Dependencies and Integration Points

It integrates a selftests subdirectory with the generic vsock test suite and kselftest's `lib.mk`. The runtime script expects `vsock_test` to appear next to it.

## Risks and Edge Cases

The source dependency uses `wildcard` over C and header files, but changes in delegated Makefile logic or generated dependencies may not be visible here. Build failures in `tools/testing/vsock` surface as failures of this wrapper target.

## Test Signals

The main signal is that `$(OUTPUT)/vsock_test` exists and is executable, and kselftest enumerates `vmtest.sh` as the test program.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vsock/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vsock/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vsock/config

## Purpose

`config` is the kernel configuration fragment used by the vsock VM test harness when `vmtest.sh -b` asks virtme-ng to generate a test kernel config. It enables VM boot support, tracing/BPF, networking, virtio, multiple vsock transports, filesystems, and the i6300esb watchdog used by the test environment.

## Important APIs, Types, and Functions

This is declarative Kconfig input rather than executable code. Important symbols include `CONFIG_VSOCKETS`, `CONFIG_VSOCKETS_DIAG`, `CONFIG_VSOCKETS_LOOPBACK`, `CONFIG_VMWARE_VMCI_VSOCKETS`, `CONFIG_VIRTIO_VSOCKETS`, `CONFIG_HYPERV_VSOCKETS`, `CONFIG_VHOST_VSOCK`, `CONFIG_VIRTIO_NET`, `CONFIG_NET_9P`, `CONFIG_9P_FS`, `CONFIG_KVM_GUEST`, `CONFIG_KVM_INTEL`, `CONFIG_KVM_AMD`, `CONFIG_FW_CFG_SYSFS`, `CONFIG_DEBUG_FS`, `CONFIG_SECURITYFS`, and `CONFIG_I6300ESB_WDT`.

## Control Flow

The fragment is consumed by `vng --kconfig --config ...` from `vmtest.sh`. virtme-ng merges the requested symbols with architecture defaults and later builds the kernel. Runtime scripts rely on the resulting kernel to expose vsock, network namespace, virtio, SSH/9p support, and diagnostics.

## State and Persistence Behavior

The file has no runtime state. It influences the generated `.config` and built kernel image in the caller's kernel tree.

## Dependencies and Integration Points

It integrates the VM test with virtme-ng, QEMU, virtio devices, vsock transport modules, debug/sysfs interfaces, and ordinary guest networking/storage facilities. The selected symbols are broader than vsock alone because the harness also needs SSH, user networking, 9p/shared directories, and diagnostics.

## Risks and Edge Cases

Some symbols are architecture- or dependency-sensitive and may be ignored if prerequisites are unavailable. Enabling several vsock transports broadens coverage but can also change module probing and warning surface. This fragment is not a minimal production config.

## Test Signals

A useful validation signal is that `vng --kconfig --config tools/testing/selftests/vsock/config` produces a bootable kernel where `vmtest.sh` can load/use virtio-vsock, loopback vsock, net namespaces, SSH, debugfs, and dmesg checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vsock/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vsock/vmtest.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vsock/vmtest.sh

## Purpose

`vmtest.sh` is a KTAP-producing integration harness for vsock behavior in virtual machines and network namespaces. It boots virtme-ng/QEMU guests with a fixed vhost-vsock CID, runs `vsock_test` in host and guest roles, validates loopback and cross-namespace visibility rules, checks same-CID VM admission rules, verifies namespace deletion does not break established sockets, and fails tests on new vsock-related kernel warnings or oopses.

## Important APIs, Types, and Functions

The script sources `../kselftest/ktap_helpers.sh` for `KSFT_*` status codes. Important constants are `VSOCK_TEST`, `TEST_GUEST_PORT`, `TEST_HOST_PORT`, `SSH_HOST_PORT`, `VSOCK_CID`, wait intervals, `QEMU_TEST_PORT_FWD`, `QEMU_SSH_PORT_FWD`, and `KERNEL_CMDLINE`. `TEST_NAMES`, `TEST_DESCS`, `USE_SHARED_VM`, and `NS_MODES` drive discovery and scheduling. Core helpers include `check_result()`, `add_namespaces()`, `init_namespaces()`, `del_namespaces()`, `vm_ssh()`, `check_deps()`, `check_vng()`, `check_socat()`, `handle_build()`, `setup_home()`, `create_pidfile()`, `terminate_pidfiles()`, `vm_start()`, `vm_wait_for_ssh()`, `wait_for_listener()`, `vm_vsock_test()`, `host_vsock_test()`, `vm_dmesg_check()`, `run_shared_vm_tests()`, and `run_ns_tests()`.

## Control Flow

Argument parsing handles `-b` for building the current kernel, `-q` for QEMU binary selection, `-v` for verbose logs, and optional test names. Setup validates dependencies, supported virtme-ng versions, socat vsock/unix support, optionally builds the kernel, creates an SSH key and test home, and prints a KTAP plan. Shared VM tests boot one guest in the initial namespace and run host-client, guest-client, and loopback scenarios. Namespace tests create parent namespaces with `child_ns_mode` set to global or local, create child namespaces, run each selected test, and tear namespaces down between tests. Individual tests start VMs in specific namespaces, bridge TCP or UNIX sockets with socat where needed, run `vsock_test` or socat probes, compare expected success/failure, and inspect dmesg warning/oops counters before and after.

## State and Persistence Behavior

The script creates temporary logs under `/tmp`, a temporary home directory with an SSH key and copied `vsock_test`, temporary QEMU pidfiles, transient network namespaces, pid-tracked background socat/vng processes, and guest state. `trap cleanup EXIT` kills pidfile-tracked processes, deletes namespaces, and removes the temporary home. It does not persist test results except the printed log path and any external build artifacts created by `-b`.

## Dependencies and Integration Points

Dependencies include `vng`, QEMU, busybox, `ssh`, `ss`, `socat` with vsock and unix support, `nsenter`, `pkill`, `ip netns`, the built `vsock_test` binary, host permissions to manage network namespaces, and a kernel with vsock namespace sysctls. It integrates with QEMU user networking, vhost-vsock PCI, virtme-init SSH conventions, `/proc/sys/net/vsock/ns_mode`, `/proc/sys/net/vsock/child_ns_mode`, guest dmesg, and kselftest KTAP output.

## Risks and Edge Cases

The harness is environment-sensitive: missing root privileges, unavailable namespace support, port conflicts on 2222/50000/50001, unsupported virtme-ng behavior, or socat without vsock support cause skips or failures. Some tests depend on fixed CID `1234` and fixed host ports. Several failure tests infer isolation by checking that `TEST` was not delivered, so timeouts and listener readiness matter. Dmesg warning matching is limited to warnings containing `vsock`.

## Test Signals

Pass signals are KTAP `ok` lines for selected tests, successful shared VM startup, successful `vsock_test` client/server exchanges where expected, failed socat delivery for disallowed namespace combinations, successful same-CID boot only for allowed local/global combinations, preserved socket data after namespace deletion, and no increase in host or guest oops/vsock warning counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vsock/vmtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/watchdog/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/watchdog/Makefile

## Purpose

This Makefile registers `watchdog-test` as the generated watchdog selftest program.

## Important APIs, Types, and Functions

It sets `TEST_GEN_PROGS := watchdog-test` and includes `../lib.mk`, relying on the standard kselftest build rules to compile `watchdog-test.c`.

## Control Flow

The kselftest build includes this directory, compiles `watchdog-test.c` into the output directory, and treats the resulting executable as a generated test program.

## State and Persistence Behavior

Only normal build artifacts are produced under the kselftest output directory.

## Dependencies and Integration Points

It depends on `lib.mk`, the userspace compiler, and kernel UAPI headers for watchdog ioctls.

## Risks and Edge Cases

There is no custom dependency logic; if `watchdog-test.c` needs extra libraries or flags, they must be supplied by common rules or added here.

## Test Signals

The signal is a built executable named `watchdog-test` included in the kselftest output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/watchdog/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/watchdog/watchdog-test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/watchdog/watchdog-test.c

## Purpose

`watchdog-test.c` is an interactive and scripted watchdog UAPI exerciser. It opens a watchdog device, validates `WDIOC_GETSUPPORT`, allows left-to-right ioctl operations for status, boot status, enable/disable, timeout, pretimeout, time-left, temperature, and info, and can run a keepalive loop until terminated.

## Important APIs, Types, and Functions

The program uses Linux watchdog ioctls from `<linux/watchdog.h>`: `WDIOC_GETSUPPORT`, `WDIOC_KEEPALIVE`, `WDIOC_GETBOOTSTATUS`, `WDIOC_SETOPTIONS`, `WDIOC_GETSTATUS`, `WDIOC_GETTEMP`, `WDIOC_SETTIMEOUT`, `WDIOC_GETTIMEOUT`, `WDIOC_SETPRETIMEOUT`, `WDIOC_GETPRETIMEOUT`, and `WDIOC_GETTIMELEFT`. Command-line parsing is via `getopt_long()` with options such as `--file`, `--info`, `--status`, `--bootstatus`, `--disable`, `--enable`, `--pingrate`, and timeout-related options. `print_status()` and `print_boot_status()` decode status bitmasks. `term()` and the `end` path write the magic close character `V`.

## Control Flow

The first getopt pass extracts the device path, defaulting to `/dev/watchdog`. The program opens it write-only, verifies watchdog support with `WDIOC_GETSUPPORT`, resets `optind`, then processes all options left-to-right so users can disable, reconfigure, and enable in one command. One-shot operations set `oneshot`, causing the program to write `V`, close, and exit. Without a one-shot request, the program requires `WDIOF_KEEPALIVEPING`, registers signal handlers, and loops forever calling `WDIOC_KEEPALIVE` and sleeping `ping_rate` seconds.

## State and Persistence Behavior

The program mutates the system watchdog device. It may enable or disable hardware, change timeout/pretimeout values, and keep the timer alive. On exit and signal handling it writes `V` to request magic close when supported. No local files are persisted.

## Dependencies and Integration Points

It depends on a watchdog device node, sufficient privileges, watchdog core UAPI, and driver support for the requested ioctls. It is designed to run against hardware watchdogs or software watchdogs such as `softdog`.

## Risks and Edge Cases

Misuse can reboot or power-cycle the machine if the watchdog is enabled and not kept alive. `SIGKILL` cannot actually be caught despite being registered. The program opens the device `O_WRONLY`, so driver-specific ioctls must tolerate that. Some status descriptions mix option and status bit namespaces, reflecting historical watchdog API conventions.

## Test Signals

Useful pass signals include successful support validation, correct status/bootstatus decoding, successful enable/disable and timeout operations when supported, expected errors for unsupported ioctls, periodic dots from keepalive, and successful magic-close write on exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/watchdog/watchdog-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/wireguard/netns.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/wireguard/netns.sh

## Purpose

`netns.sh` is WireGuard's large network-namespace integration stress test. It builds multiple namespace topologies, configures WireGuard peers with generated keys, and validates IPv4/IPv6 transport, throughput, MTU behavior, roaming, crypto routing, nested WireGuard, NAT traversal, policy routing, source-address stickiness, netlink split responses, key handling, low-order point rejection behavior, and namespace lifetime cleanup.

## Important APIs, Types, and Functions

The script uses `ip netns`, `ip -n`, `wg`, `ping`, `ping6`, `iperf3`, `ncat`, `iptables`, `ss`, `conntrack`-related sysctls, `/proc/sys/net/core/message_cost`, and `/dev/kmsg`. Helper functions include `pretty()`, `pp()`, namespace command wrappers `n0/n1/n2` and `ip0/ip1/ip2`, `waitiperf()`, `waitncatudp()`, `waitiface()`, `cleanup()`, `configure_peers()`, and `tests()`. It exports `WG_HIDE_KEYS=never` so key assertions can compare exact values.

## Control Flow

Startup creates three namespaces, creates WireGuard devices in a central namespace and moves peers into endpoint namespaces, generates four private/public key pairs plus a preshared key, and configures base peer addresses. `tests()` runs ping and iperf3 coverage for IPv4, IPv6, UDP, TCP, and parallel TCP. The script then runs many scenario blocks: IPv4 and IPv6 outer endpoints at normal and large MTU, route-MTU padding, endpoint roaming, crypto-RP filtering with more-specific allowed IPs, private-key rotation, WireGuard-over-WireGuard and routing loop checks, NAT and persistent keepalive behavior, bound-device and fwmark routing, onion routing, wg-quick-style default route policy routing, ICMP error routing through NAT, source-address stickiness, persistent keepalives on interface/private-key activation, large netlink/IPC allowed-ips responses, key clearing and public-key derivation behavior, low-order public-key behavior, dst-cache cleanup across namespace deletion, and circular namespace reference cleanup.

## State and Persistence Behavior

All state is intended to be transient: namespaces named with the shell pid, WireGuard/veth/dummy devices, iptables rules, sysctls, generated keys, background iperf/ncat processes, and kernel log observations. `cleanup()` restores `message_cost`, deletes devices and namespaces, kills namespace pids, and exits.

## Dependencies and Integration Points

The script requires root privileges, WireGuard kernel support, `wireguard-tools`, iproute2, iptables legacy behavior for some commands, iperf3, nmap `ncat`, ping utilities, netns support, and optional modules such as `vsock_loopback` are not relevant here. It integrates with WireGuard netlink APIs, routing tables/rules, netfilter NAT/filter/mangle tables, DSA-free ordinary network namespaces, and kernel object lifetime logs.

## Risks and Edge Cases

The test intentionally changes global `/proc/sys/net/core/message_cost`, manipulates iptables, creates many routes/rules, and can be disruptive on a non-isolated host. Some assertions depend on exact transfer byte counters and endpoint string formatting. The routing-loop section prints a prominent warning but continues for a known unsolved architecture behavior. Cleanup depends on namespace names being unique and deletion succeeding.

## Test Signals

Pass signals are command success under `set -e`, successful pings/iperf runs, expected WireGuard transfer counters and latest-handshake timestamps, expected endpoint strings after roaming/source routing, dropped packets in negative crypto routing cases, successful large allowed-ips enumeration counts, no packets sent to low-order peers, and `/dev/kmsg` evidence that created WireGuard objects are destroyed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/wireguard/netns.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/wireguard/qemu/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/wireguard/qemu/Makefile

## Purpose

This Makefile builds and runs the WireGuard QEMU selftest environment. It downloads fixed userspace/toolchain distfiles, builds a minimal cross-compiled userspace and kernel with an initramfs containing `init`, `netns.sh`, and required tools, then boots the result under QEMU and checks for a `success` marker.

## Important APIs, Types, and Functions

The Makefile defines download macros `tar_download` and `file_download`, architecture mapping variables such as `CHOST`, `QEMU_ARCH`, `KERNEL_ARCH`, `KERNEL_BZIMAGE`, `QEMU_MACHINE`, and build variables such as `KERNEL_PATH`, `BUILD_PATH`, `DISTFILES_PATH`, `NR_CPUS`, `CROSS_COMPILE`, `CC`, `CFLAGS`, and `LDFLAGS`. Targets build iperf3, bash, iproute2 `ip`/`ss`, iptables legacy multi-call binary, nmap `ncat`, iputils `ping`, wireguard-tools `wg`, the local `init.c`, the initramfs cpio spec, kernel config, kernel image, and `qemu`.

## Control Flow

The default target is `qemu`. Distfile targets download from `download.wireguard.com` first and upstream mirrors second, then verify SHA-256. Architecture conditionals select the cross toolchain, kernel image path, QEMU machine/cpu options, and special command-line handling. The initramfs spec embeds `/init`, `/init.sh` from `../netns.sh`, tool binaries, libc, symlinks, and device nodes. Kernel config is produced by `allnoconfig` plus merges of `kernel.config`, architecture config, initramfs settings, and optional debug config. The QEMU target boots the image for up to 20 minutes, writes a result virtio/serial chardev to `$(BUILD_PATH)/result`, and greps for `success`.

## State and Persistence Behavior

Persistent build cache lives under `$(BUILD_PATH)`, downloaded archives under `$(DISTFILES_PATH)`, and optional `ccache` under `$(CCACHE_DIR)`. `clean`, `distclean`, and `cacheclean` remove increasingly broad state. The target writes `$(BUILD_PATH)/result` for QEMU success detection.

## Dependencies and Integration Points

It depends on host `make`, `gcc`, `wget`, `flock`, `sha256sum`, `tar`, QEMU for the selected architecture, kernel source tree, and optional `ccache`. It integrates with kernel header installation, cross musl toolchains, autotools/configure-based packages, and QEMU serial/virtio console success reporting.

## Risks and Edge Cases

The Makefile downloads and builds old pinned userspace package versions, so upstream URL changes or checksum mismatch will fail builds. It uses `sed -i` patches on extracted packages. Cross-architecture support is extensive but brittle around host/target matching, KVM availability, QEMU machine support, and architecture-specific config fragments. `qemu` requires the guest to write `success`; otherwise the final grep fails even if boot mostly worked.

## Test Signals

Pass signals are successful verified downloads, installed toolchain, built static userspace tools, generated initramfs spec, merged kernel config, built kernel image, QEMU exiting within timeout, and `success` present in `$(BUILD_PATH)/result`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/wireguard/qemu/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/wireguard/qemu/init.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/wireguard/qemu/init.c

## Purpose

`init.c` is the PID 1 program for the WireGuard QEMU test initramfs. It prepares a minimal guest environment, verifies WireGuard module selftests, launches `/init.sh`, reports success through a command-line-selected device, optionally scans kmemleak, and reboots/powers off.

## Important APIs, Types, and Functions

Important functions are `poweroff()`, `panic()`, `print_banner()`, `seed_rng()`, `set_time()`, `mount_filesystems()`, `enable_logging()`, `kmod_selftests()`, `launch_tests()`, `ensure_console()`, `clear_leaks()`, and `check_leaks()`. It uses `reboot(RB_AUTOBOOT)`, `mount()`, `symlink()`, `uname()`, `getrandom()`, `RNDADDTOENTCNT`, `stime()`, `/proc/kmsg`, `/proc/cmdline`, `/sys/kernel/debug/kmemleak`, `sendfile()`, and `fork()/execl()/waitpid()`.

## Control Flow

`main()` opens the console, prints a banner, mounts devtmpfs/proc/sysfs/tmpfs/debugfs, seeds RNG entropy if needed, sets a fake time if wall clock is zero, parses WireGuard module selftest messages from `/proc/kmsg`, enables verbose kernel logging, clears kmemleak, forks and execs `/init.sh`, checks child status, writes `success\n` to the `wg.success=` device named on the kernel command line if the script exited zero, scans kmemleak, and reboots. Any unrecoverable setup failure calls `panic()` and then `poweroff()`.

## State and Persistence Behavior

State is entirely in the ephemeral guest: mounted pseudo filesystems, fake time, kernel printk settings, RNG entropy count, kmemleak state, and the success marker device. No persistent disk is required.

## Dependencies and Integration Points

It depends on the initramfs containing `/init.sh`, `/dev/console`, devtmpfs/proc/sysfs/debugfs support, WireGuard module selftest printk output, and a kernel command-line `wg.success=` token generated by the QEMU Makefile's chardev setup.

## Risks and Edge Cases

The RNG seeding path intentionally fabricates entropy for the test VM. `kmod_selftests()` assumes WireGuard emits expected pass lines before the URL banner appears. Success reporting depends on mutating a `wg.success=` token into `/dev/...`; malformed cmdline causes panic. Kmemleak scanning can fail the run after functional tests pass.

## Test Signals

Pass signals include visible banner/setup messages, all WireGuard module selftests ending in `: pass`, `/init.sh` exit status zero, successful write of `success\n` to the result device, and no kmemleak output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/wireguard/qemu/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/Makefile

## Purpose

The x86 selftests Makefile selects, builds, and registers 32-bit and 64-bit x86 userspace ABI tests. It detects compiler support for i386, x86_64, and `-no-pie`, builds target-specific binaries, adds assembly helper dependencies where needed, and warns when 32-bit build support is missing on a 64-bit host.

## Important APIs, Types, and Functions

Important variables include `CAN_BUILD_I386`, `CAN_BUILD_X86_64`, `CAN_BUILD_WITH_NOPIE`, `TARGETS_C_BOTHBITS`, `TARGETS_C_32BIT_ONLY`, `TARGETS_C_64BIT_ONLY`, `TARGETS_C_32BIT_NEEDED`, `BINARIES_32`, `BINARIES_64`, `CFLAGS`, `EXTRA_CFLAGS`, and `EXTRA_FILES`. It uses `check_cc.sh` to probe compilation. The `extra-files` macro attaches assembly or C helper files to specific output targets.

## Control Flow

If 32-bit compilation works, `all` depends on `all_32`, 32-bit binaries are added to `TEST_PROGS`, and `-DCAN_BUILD_32` is set. If 64-bit compilation works, the same happens for `all_64` with `-DCAN_BUILD_64`. When both modes work, 32-bit-needed tests also get 64-bit builds. Pattern rules compile `%.c` to `$(OUTPUT)/%_32` with `-m32` and `$(OUTPUT)/%_64` with `-m64`. Special flags make `check_initial_reg_state` static with a custom entry point, mark `nx_stack` non-executable, prevent AVX codegen in `avx`, and include `xstate.c` for AVX/AMX/APX.

## State and Persistence Behavior

The Makefile writes only compiled binaries under `$(OUTPUT)` and cleans them through `EXTRA_CLEAN`.

## Dependencies and Integration Points

It integrates with `../lib.mk`, kernel selftest headers, multilib compiler/runtime support, `helpers.h`, and x86 assembly helper files. Several generated binaries depend on system calls or CPU features at runtime.

## Risks and Edge Cases

Reduced multilib support silently reduces coverage after printing a warning. `-no-pie` is only added if supported because some tests use absolute-address assembly. Clang requires a warning suppression for `-no-pie` in compile+link invocations. The target lists must stay aligned with actual source files and architecture restrictions.

## Test Signals

Signals include `check_cc.sh` returning `1` for supported modes, generated `_32` and `_64` binaries under `$(OUTPUT)`, the 32-bit warning only when expected, and successful special-target compilation with required helper files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/amx.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/amx.c

## Purpose

`amx.c` validates userspace AMX XTILEDATA xstate behavior on x86_64. It checks that XTILEDATA permission is denied before a sufficiently large signal stack is installed, that `ARCH_REQ_XCOMP_PERM` updates permissions correctly, that permission and compatible altstack state survive fork, that tile data is not inherited across fork, and then delegates to generic xstate context/signal/ptrace tests for XTILEDATA.

## Important APIs, Types, and Functions

The file depends on `xstate.h` helpers such as `alloc_xbuf()`, `clear_xstate_header()`, `set_xstatebv()`, `set_rand_data()`, `xrstor()`, `xsave()`, `get_fpx_sw_bytes()`, `get_fpx_sw_bytes_features()`, `get_xstate_info()`, and `test_xstate()`. It uses `arch_prctl` codes `ARCH_GET_XCOMP_SUPP`, `ARCH_GET_XCOMP_PERM`, and `ARCH_REQ_XCOMP_PERM`. Important local functions are `handle_noperm()`, `xrstor_safe()`, `load_rand_tiledata()`, `validate_req_xcomp_perm()`, `validate_xcomp_perm()`, `test_dynamic_sigaltstack()`, `test_dynamic_state()`, `validate_tiledata_regs_changed()`, and `test_fork()`.

## Control Flow

`main()` skips unless `ARCH_GET_XCOMP_SUPP` advertises tile config and tile data. It obtains XTILEDATA size/offset, allocates a stashed XSAVE buffer, and installs a SIGILL handler. `test_dynamic_state()` forks so permission experiments cannot contaminate later tests; the child confirms XTILEDATA load fails without permission, installs a small altstack and expects permission request failure, installs a large altstack and expects success, rejects later shrinking below the AMX requirement, confirms XTILEDATA can load, and validates inheritance in a grandchild. Back in the original process, `main()` requests XTILEDATA permission, runs `test_fork()` to confirm child tile registers differ from parent-loaded tile data, then calls generic `test_xstate(XFEATURE_XTILEDATA)`.

## State and Persistence Behavior

State is process-local xstate, signal-handler state, altstack mappings, and forked process state. There is no file persistence. The test deliberately changes the process's dynamic xstate permission and signal stack configuration.

## Dependencies and Integration Points

It requires x86_64, CPU and kernel AMX support, dynamic xstate permission support, valid `AT_MINSIGSTKSZ`, signal frame xstate metadata, and the local xstate selftest library. It integrates with kselftest skip/pass/fail conventions through `helpers.h`/`kselftest`.

## Risks and Edge Cases

The SIGILL handler advances RIP by three bytes to skip the expected `XRSTOR`; this depends on the emitted instruction length. Signal-safe output is avoided with a static buffer, but test diagnostics still depend on handler sequencing. If `AT_MINSIGSTKSZ` is absent, sigaltstack-specific coverage is skipped. Forking isolates some permission changes but complicates failure attribution.

## Test Signals

Pass signals include expected SIGILL/`ILL_ILLOPC` before permission, valid signal xstate size/mask without XTILEDATA, failed permission on too-small altstack, successful permission on large altstack, failure to shrink altstack afterward, inherited permission in the grandchild, changed XTILEDATA after fork, and successful generic xstate tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/amx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/apx.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/apx.c

## Purpose

`apx.c` is a minimal x86_64 xstate selftest entry point for APX state. It delegates all behavior to the generic xstate test framework.

## Important APIs, Types, and Functions

The file includes `xstate.h` and calls `test_xstate(XFEATURE_APX)` from `main()`.

## Control Flow

Execution immediately runs the generic xstate test suite for `XFEATURE_APX`. Feature probing, skip logic, context-switch validation, ptrace validation, and signal behavior are handled by `xstate.c`/`xstate.h`.

## State and Persistence Behavior

State is limited to process register/xstate manipulation performed by the xstate helper framework. There is no persistence.

## Dependencies and Integration Points

It depends on the x86 selftests build adding `xstate.c`, APX-aware kernel/CPU support, and generic xstate helper code.

## Risks and Edge Cases

The source itself has no local checks; all robustness depends on the shared xstate harness correctly handling unsupported APX environments.

## Test Signals

Pass/skip/fail signals are emitted by `test_xstate(XFEATURE_APX)`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/apx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/avx.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/avx.c

## Purpose

`avx.c` is a compact xstate test driver for AVX and AVX-512 register components. It validates YMM, opmask, high ZMM, and high-16 ZMM xstate handling through the shared xstate framework.

## Important APIs, Types, and Functions

The file includes `xstate.h` and calls `test_xstate()` for `XFEATURE_YMM`, `XFEATURE_OPMASK`, `XFEATURE_ZMM_Hi256`, and `XFEATURE_Hi16_ZMM`.

## Control Flow

`main()` sequentially invokes the generic xstate test for each listed feature. The Makefile compiles this target with `-mno-avx -mno-avx512f` so compiler-generated vector instructions do not accidentally interfere with test-controlled xstate.

## State and Persistence Behavior

Only process CPU xstate is manipulated. There is no persistent state.

## Dependencies and Integration Points

It depends on the shared `xstate.c` support, CPU/kernel support for the relevant xfeatures, and x86 selftest build flags.

## Risks and Edge Cases

Unsupported features must be skipped by the shared xstate harness. Because tests run sequentially in one process, the helper must correctly reset or isolate per-feature state.

## Test Signals

Signals are the generic xstate harness results for YMM, opmask, ZMM high-256, and high-16 ZMM state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/avx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/bugs/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/bugs/Makefile

## Purpose

This Makefile registers Python kselftests for x86 bug mitigation behavior, focused here on indirect target selection (ITS).

## Important APIs, Types, and Functions

It sets `TEST_PROGS := its_sysfs.py its_permutations.py its_indirect_alignment.py its_ret_alignment.py` and `TEST_FILES := common.py`, then includes `../../lib.mk`.

## Control Flow

kselftest copies/runs the four Python programs and installs `common.py` as supporting data. Build compilation is not involved.

## State and Persistence Behavior

Only kselftest output/copy state is produced. The tests themselves may create runtime logs, but this Makefile does not.

## Dependencies and Integration Points

It integrates Python tests with kselftest. The Python tests depend on kernel vulnerability sysfs, optional vmlinux/debug data, drgn, pyelftools, capstone, and virtme-ng.

## Risks and Edge Cases

Missing `common.py` would break all tests. Dependencies are runtime Python modules rather than Makefile dependencies, so failures are handled as test skips or runtime errors by scripts.

## Test Signals

kselftest should enumerate all four Python programs and make `common.py` available in the test directory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/bugs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/bugs/common.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/bugs/common.py

## Purpose

`common.py` centralizes helper routines for Python x86 bug mitigation kselftests. It reads CPU/sysfs/cmdline state, reports kselftest results, parses vmlinux patch-site sections, disassembles x86 instructions, opens the live kernel through drgn, and skips tests when optional Python dependencies are absent.

## Important APIs, Types, and Functions

File readers include `read_file()`, `cpuinfo_has()`, `cmdline_has*()`, `get_sysfs()`, and `sysfs_has*()`. Result helpers are `bug_check_pass()`, `bug_check_fail()`, `bug_status_unknown()`, and `basic_checks_sufficient()`. Binary/kernel helpers are `get_section_info()`, `get_patch_sites()`, `get_instruction_from_vmlinux()`, `init_capstone()`, `get_runtime_kernel()`, and `check_dependencies_or_skip()`.

## Control Flow

Individual tests import this module, run basic vulnerability/status checks, and then use these helpers to inspect either text state or binary/runtime patch state. `get_patch_sites()` reads 32-bit relative offsets from a section such as `.return_sites` or `.retpoline_sites`. `get_instruction_from_vmlinux()` maps a virtual address into the `.text` section and returns the capstone instruction at that address. `check_dependencies_or_skip()` imports each required module and exits through `ksft.finished()` after a skip if a dependency is missing.

## State and Persistence Behavior

The module reads `/proc/cpuinfo`, `/proc/cmdline`, `/sys/devices/system/cpu/vulnerabilities/*`, vmlinux files, and live kernel memory through drgn. It does not persist state itself.

## Dependencies and Integration Points

It depends on Python kselftest `ksft`, optional `elftools`, `capstone`, and `drgn`, and kernel debug/vulnerability interfaces. It is shared by ITS sysfs, permutation, indirect alignment, and return alignment tests.

## Risks and Edge Cases

`sysfs_has()` assumes `get_sysfs()` returns a string; a missing vulnerability file can lead to membership tests on `None`. Section and symbol assumptions are x86_64-specific. drgn access to the live kernel requires permissions and debug symbols.

## Test Signals

Useful signals are clean dependency skips for missing modules, accurate pass/fail messages with found/expected mitigation text, successful section lookup with offsets, and valid capstone disassembly for runtime patch-site comparisons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/bugs/common.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/bugs/its_indirect_alignment.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/bugs/its_indirect_alignment.py

## Purpose

`its_indirect_alignment.py` validates indirect branch/call patch sites under the x86 indirect target selection mitigation. It compares `.retpoline_sites` from vmlinux with live instructions read from `/proc/kcore` via drgn, checking that unsafe sites are patched to aligned ITS thunks or otherwise safe direct branches.

## Important APIs, Types, and Functions

The script imports `ksft` and `common` helpers, uses pyelftools `ELFFile`, drgn `program_from_kernel()`, `identify_address()`, and capstone disassembly. It consumes the sysfs vulnerability `indirect_target_selection`, skips if aligned thunks are not active or Spectre v2 retpolines are deployed, optionally copies a user-supplied vmlinux into `/usr/lib/debug/lib/modules/$(uname -r)/vmlinux`, and reads symbols `__retpoline_sites` and `__x86_indirect_its_thunk_r15`.

## Control Flow

After skip/dependency checks, the script locates `.retpoline_sites`, reads its relative patch-site offsets, maps the vmlinux section base to the live kernel `__retpoline_sites` address, and iterates over each site. For each site it prints vmlinux and kcore instructions, computes whether the instruction end is in a safe half of the 64-byte region, and passes safe sites immediately. Unsafe sites pass if their immediate target resolves to an ITS thunk at a safe address or to a direct branch that does not require an ITS thunk; otherwise they are failed or marked unknown on unexpected operands/exceptions.

## State and Persistence Behavior

The script may copy a supplied vmlinux into `/usr/lib/debug/lib/modules/<release>/vmlinux`. Otherwise it only reads sysfs, vmlinux, and live kernel memory and prints kselftest output.

## Dependencies and Integration Points

It depends on aligned ITS mitigation being active, no retpoline deployment for this path, drgn, pyelftools, capstone, accessible kernel debug symbols, and readable live kernel memory.

## Risks and Edge Cases

The script assumes `.retpoline_sites`, `__retpoline_sites`, and ITS thunk symbols exist and match the running kernel. Operand parsing is narrow, and some unexpected instruction forms are classified unknown. Copying vmlinux via `os.system()` does not shell-quote the supplied path.

## Test Signals

Pass signals include zero failed sites, per-site diagnostics showing safe address alignment or acceptable thunk/direct branch targets, and a final kselftest pass when `tests_failed == 0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/bugs/its_indirect_alignment.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/bugs/its_permutations.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/bugs/its_permutations.py

## Purpose

`its_permutations.py` boots many virtme-ng kernels with combinations of `indirect_target_selection=`, `retbleed=`, and `spectre_v2=` command-line options, then runs `its_sysfs.py` inside each guest to validate sysfs mitigation reporting.

## Important APIs, Types, and Functions

It imports `subprocess`, `itertools`, `re`, `shutil`, `ksft`, and `common`. Important data are `default_kparam`, `BOOT_CMD`, `input_options`, and `TEST` pointing to `its_sysfs.py`. `pretty_print()` colorizes TAP and diagnostic output.

## Control Flow

The script skips if the host is not affected or if `vng` is unavailable. It computes the Cartesian product of all option values, sets a kselftest plan for the number of combinations, and for each combination builds a `vng --run <bzImage>` command with default panic/debugging parameters plus the tested mitigation parameters. It appends `-- <TEST>` to run the sysfs checker in the guest, waits for completion, reports pass on return code zero and fail otherwise, colorizes the captured output, appends it to `logs`, and writes `logs.txt` at the end.

## State and Persistence Behavior

The script writes `logs.txt` in the current working directory. virtme-ng may create its own temporary VM state. No kernel settings are changed on the host except through guest boots.

## Dependencies and Integration Points

It depends on virtme-ng, a built `arch/x86/boot/bzImage` relative to the test directory, `its_sysfs.py`, and the Python kselftest framework. It integrates command-line mitigation permutations with guest sysfs validation.

## Risks and Edge Cases

The command is executed through `shell=True` and is assembled as a string. Runtime is proportional to all option combinations, so it is expensive. The hardcoded bzImage path assumes an in-tree kernel build. `logs.txt` is overwritten in the working directory.

## Test Signals

Pass signals are one kselftest result per option combination, guest return code zero, readable pretty-printed `its_sysfs.py` output, and a final `ksft.finished()` summary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/bugs/its_permutations.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/bugs/its_ret_alignment.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/bugs/its_ret_alignment.py

## Purpose

`its_ret_alignment.py` validates return-site patching for x86 indirect target selection mitigation. It inspects `.return_sites` in vmlinux and live kernel memory to ensure unsafe return instructions have been patched to jumps or otherwise do not remain unsafe returns.

## Important APIs, Types, and Functions

The script uses `common` helpers for sysfs, section parsing, patch-site offsets, capstone setup, and drgn runtime access. It reads symbols `__return_sites` and `its_return_thunk`, uses `ELFFile` for vmlinux `.text`, and uses `identify_address()` for diagnostics.

## Control Flow

The script skips unless the `indirect_target_selection` sysfs text contains `Aligned branch/return thunks`. It checks Python dependencies, optionally installs a supplied vmlinux, locates `.return_sites`, reads all patch-site offsets, opens the running kernel through drgn, and iterates all sites. For each site it disassembles the vmlinux and live instruction, computes whether the live instruction ends in the safe address half, and passes safe sites. Unsafe sites pass if the live instruction is a jump, skip if it is no longer a return, and fail if an unsafe return remains. Exceptions count as unknown.

## State and Persistence Behavior

Like the indirect alignment test, it may copy a supplied vmlinux into `/usr/lib/debug/lib/modules/<release>/vmlinux`. Otherwise it only reads kernel state and prints test output.

## Dependencies and Integration Points

It requires aligned ITS return mitigation, vmlinux debug data matching the running kernel, drgn, pyelftools, capstone, and access to live kernel memory/symbols.

## Risks and Edge Cases

The script assumes section/symbol names and address offsets match exactly. Unknown disassembly or missing instructions are counted separately but do not by themselves fail unless `tests_failed` is nonzero. The optional vmlinux copy path is not shell-quoted.

## Test Signals

Pass signals are zero failed return sites, per-site diagnostics showing safe alignment or jump patching, and a final pass message `All ITS return thunk sites passed.`
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/bugs/its_ret_alignment.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/bugs/its_sysfs.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/bugs/its_sysfs.py

## Purpose

`its_sysfs.py` validates the `/sys/devices/system/cpu/vulnerabilities/indirect_target_selection` status string against CPU features and kernel command-line mitigation choices.

## Important APIs, Types, and Functions

The script imports all helpers from `common.py`, reads `bug = "indirect_target_selection"`, and defines expected strings for aligned thunks, retpoline plus RSB stuffing, VM-exit-only vulnerability, and vulnerable state. `check_mitigation()` implements the policy matrix. It uses `basic_checks_sufficient()` for common `Not affected` and explicit disabled/vulnerable cases.

## Control Flow

The script prints a kselftest header, sets a one-test plan, prints the found mitigation string, and then either lets `basic_checks_sufficient()` report a result or runs `check_mitigation()`. The detailed checker compares the exact mitigation string against command-line options such as `indirect_target_selection=stuff`, `indirect_target_selection=vmexit`, Spectre v2 retpoline status, retbleed stuffing status, and CPU feature text `its_native_only`.

## State and Persistence Behavior

The script is read-only. It reads `/proc/cpuinfo`, `/proc/cmdline`, and vulnerability sysfs files.

## Dependencies and Integration Points

It depends on the Python kselftest framework and the shared `common.py` helpers. It is also used as the guest payload by `its_permutations.py`.

## Risks and Edge Cases

The logic uses exact mitigation strings, so wording changes in sysfs can produce unknown/fail results. Multiple independent `if` blocks in `check_mitigation()` can fall through to `bug_status_unknown()` after a failure path unless an earlier branch returns. Missing sysfs files are handled through common helper behavior.

## Test Signals

The expected signal is one kselftest result: pass for matching mitigation policy, fail with found/expected diagnostics for inconsistent sysfs text, or unknown status diagnostics for unrecognized strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/bugs/its_sysfs.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/check_cc.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/check_cc.sh

## Purpose

`check_cc.sh` is a tiny compiler capability probe used by the x86 selftests Makefile to decide whether a compiler can build a given test program with a given set of flags.

## Important APIs, Types, and Functions

It accepts `CC`, `TESTPROG`, and remaining compiler flags. It invokes `$CC -o /dev/null "$TESTPROG" -O0 "$@"` with stderr suppressed.

## Control Flow

If `CC` is non-empty and the compile/link command succeeds, it prints `1`; otherwise it prints `0`. It always exits zero so Makefile variable assignment can consume the printed capability bit without failing the build.

## State and Persistence Behavior

No files are persisted because the output path is `/dev/null`.

## Dependencies and Integration Points

It depends on a shell and the selected compiler. The Makefile uses it for 32-bit, 64-bit, and `-no-pie` probes.

## Risks and Edge Cases

Compiler paths containing shell metacharacters are not protected because `$CC` is intentionally expanded as a command. Linker/runtime library failures are treated the same as compiler failures.

## Test Signals

The only signal is stdout `1` or `0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/check_cc.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/check_initial_reg_state.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/check_initial_reg_state.c

## Purpose

`check_initial_reg_state.c` verifies the initial general-purpose register and flags state at process entry after `execve()`. It uses a custom assembly entry point to capture registers before libc or the dynamic loader can modify them.

## Important APIs, Types, and Functions

Global variables store captured registers: `ax`, `bx`, `cx`, `dx`, `si`, `di`, `bp`, `sp`, `flags`, and on x86_64 `r8` through `r15`. Inline assembly defines global function `real_start`, stores registers into globals, captures flags with `pushf/popf`, and jumps to `_start`. The Makefile links this test statically with `-Wl,-ereal_start -static`.

## Control Flow

At process entry, `real_start` runs first and records register state. Normal startup then calls `main()`, which fails if `sp` is zero, verifies all GPRs except stack pointer are zero, prints each unexpected value on failure, and verifies `FLAGS == 0x202`.

## State and Persistence Behavior

State is just global variables in the test process. There is no persistence.

## Dependencies and Integration Points

It depends on static linking and the Makefile's custom entry point so no interpreter destroys initial state. It integrates with x86 selftest build modes for both 32-bit and 64-bit.

## Risks and Edge Cases

The expected zero-register ABI is sensitive to kernel exec setup and architecture mode. If the binary is accidentally linked dynamically or without `real_start`, the test detects `sp == 0` or false register values.

## Test Signals

Pass signals are `[OK] All GPRs except SP are 0` and `[OK] FLAGS is 0x202`, with zero exit status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/check_initial_reg_state.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/clang_helpers_32.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/clang_helpers_32.S

## Purpose

`clang_helpers_32.S` provides a 32-bit assembly helper for tests that need segment-prefixed memory access unsupported by some clang inline assembly forms.

## Important APIs, Types, and Functions

It exports `dereference_seg_base`, which executes `mov %fs:(0), %eax` and returns. It also declares a non-executable stack note.

## Control Flow

Callers set up `%fs` to point at a known segment base, call `dereference_seg_base()`, and receive the 32-bit value at offset zero from that segment.

## State and Persistence Behavior

No state is stored in the helper. It reads through the caller's current FS segment selector/base.

## Dependencies and Integration Points

It is linked into `fsgsbase_restore_32` by the x86 Makefile.

## Risks and Edge Cases

Correctness depends entirely on the caller's segment setup. If FS is invalid, the helper can fault.

## Test Signals

The helper is validated indirectly when callers read the expected value through FS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/clang_helpers_32.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/clang_helpers_64.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/clang_helpers_64.S

## Purpose

`clang_helpers_64.S` provides 64-bit assembly helpers for segment dereference and a page-aligned syscall instruction test page.

## Important APIs, Types, and Functions

It exports `dereference_seg_base`, `test_page`, and `test_syscall_insn`. `dereference_seg_base` reads `mov %gs:(0), %rax`. `test_page` is 4096-byte aligned and filled with `0xcc` bytes except for a `syscall` instruction near the end. The assembler asserts the page is exactly one page long and emits a GNU-stack note.

## Control Flow

Segment tests call `dereference_seg_base()` after setting GS. Syscall entry tests can use `test_page`/`test_syscall_insn` to place a syscall instruction at a controlled page offset.

## State and Persistence Behavior

There is no writable state. The file contributes text symbols.

## Dependencies and Integration Points

It is linked into `fsgsbase_restore_64` and `sysret_rip_64` through the Makefile's `extra-files` macro.

## Risks and Edge Cases

The exact page layout is part of the test contract; assembler/linker changes that disturb alignment would break dependent tests. Invalid GS setup can fault the dereference helper.

## Test Signals

Signals are indirect: callers successfully read the expected GS-based value or use the syscall page at the intended layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/clang_helpers_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/corrupt_xstate_header.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/corrupt_xstate_header.c

## Purpose

`corrupt_xstate_header.c` is a regression test for kernel handling of a deliberately corrupted xstate header in a signal frame. It verifies that returning from such a signal and then scheduling does not explode or warn.

## Important APIs, Types, and Functions

`xsave_enabled()` checks CPUID leaf 1 ECX OSXSAVE. `sigusr1()` locates `uc_mcontext.fpregs`, advances to the xstate header at offset 512, and corrupts a reserved qword. `sigsegv()` prints if a segmentation fault occurs. `main()` installs handlers with `sethandler()`, pins to CPU 0, raises SIGUSR1, forks, and waits for the child.

## Control Flow

The program skips if OSXSAVE is disabled. Otherwise it pins itself, raises SIGUSR1, corrupts the signal frame xstate header in the handler, returns from the signal, then forks and waits to force scheduling on the same CPU. Success is reaching the end without crash; kernel warnings must be checked externally.

## State and Persistence Behavior

The test modifies only its own signal frame and scheduling affinity. No persistent state exists.

## Dependencies and Integration Points

It depends on x86 XSAVE signal-frame layout, CPUID support via `kselftest.h`, signal delivery, scheduler affinity, and fork/wait.

## Risks and Edge Cases

The reserved-field offset is architecture-layout-specific. The test does not parse dmesg itself, so warnings mentioned in comments are outside the binary's exit status unless the broader runner checks logs.

## Test Signals

Pass signal is normal exit after printing back-from-signal and back-in-main-thread messages. A crash, SIGSEGV, or external kernel warning indicates failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/corrupt_xstate_header.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/entry_from_vm86.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/entry_from_vm86.c

## Purpose

`entry_from_vm86.c` tests kernel entry and signal paths from vm86 mode. It exercises exceptions, syscall-like instructions, interrupt handling, VIP/IF behavior, UMIP instruction emulation, null pointer execution, and fork cleanup from a vm86-capable process.

## Important APIs, Types, and Functions

It uses `vm86(VM86_ENTER, ...)`, `struct vm86plus_struct`, VM86 return macros, signal handlers, and 16-bit inline assembly blobs. Important helpers are `sighandler()`, `do_test()`, `do_umip_tests()`, and the assembly labels `vmcode_bound`, `vmcode_sysenter`, `vmcode_syscall`, `vmcode_sti`, `vmcode_int3`, `vmcode_int80`, `vmcode_popf_hlt`, `vmcode_umip`, `vmcode_umip_str`, and `vmcode_umip_sldt`.

## Control Flow

`main()` maps executable memory at `0x10000`, copies the 16-bit vm86 test code, initializes segment registers and stack, and runs a series of `do_test()` calls. Each call sets vm86 EIP, enters vm86 mode, handles skips for unsupported/disallowed vm86, prints the exit reason, and verifies the expected VM86 type/argument unless the expected type is `-1`. UMIP tests compare emulated SMSW/SIDT/SGDT results across addressing modes and expect STR/SLDT to signal. The final null pointer case expects SIGSEGV, and a fork sanity check ensures no cleanup failure.

## State and Persistence Behavior

State is process-local mapped low memory, vm86 register state, and signal flags. No persistence exists.

## Dependencies and Integration Points

It is 32-bit-only in the Makefile and requires kernel `vm86` support and permission. It integrates with x86 signal-frame conventions and UMIP emulation behavior.

## Risks and Edge Cases

Modern 64-bit-only kernels may skip due to `ENOSYS` or `EPERM`. The test maps executable low memory at a fixed address. Some outcomes vary by CPU feature, such as SYSENTER behavior on non-SEP CPUs, and the test avoids strict checking for those cases.

## Test Signals

Pass signals are expected VM86 exit reasons for #BR, SYSCALL, STI, POPF, INT3, INT80, UMIP, and null execution, consistent UMIP emulation results, receipt of SIGSEGV for null execution, and zero accumulated errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/entry_from_vm86.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/fsgsbase.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/fsgsbase.c

## Purpose

`fsgsbase.c` is a 64-bit stress/regression test for GS base and selector semantics across `arch_prctl`, direct FSGSBASE instructions, context switches, futex-coordinated threads, LDT/GDT selector loads, and ptrace reads/writes.

## Important APIs, Types, and Functions

The test uses `ARCH_SET_GS`, `ARCH_GET_GS`, `modify_ldt`, 32-bit `set_thread_area` via `int $0x80`, futex syscalls, pthreads, ptrace `PTRACE_PEEKUSER`/`PTRACE_POKEUSER`, and signal-based base discovery. Important functions include `sigsegv()`, `sigill()`, `rdgsbase()`, `rdfsbase()`, `wrgsbase()`, `read_base()`, `check_gs_value()`, `mov_0_gs()`, `load_gs()`, `test_wrbase()`, `threadproc()`, `set_gs_and_switch_to()`, `test_unexpected_base()`, `test_ptrace_write_gs_read_base()`, and `test_ptrace_write_gsbase()`.

## Control Flow

The test first prepares shared scratch memory, runs ptrace GS/GSBASE read behavior before LDT setup, probes whether FSGSBASE instructions are enabled by catching SIGILL, and installs a SIGSEGV handler for base discovery. It verifies several `ARCH_SET_GS` values, behavior after loading selector zero, and optional scheduling. It pins to CPU 0, starts a helper thread, and runs combinations of local GS base, forced selector, and remote helper-thread GS base to verify context-switch preservation. It checks a remote unexpected-base scenario, optionally tests `wrgsbase()` preservation across switches, stops the helper thread, and finally tests ptrace writing GSBASE while preserving selector state.

## State and Persistence Behavior

State includes GS selector/base, LDT/GDT entries, futex variables, helper thread state, shared scratch mapping, ptrace child state, and CPU affinity. It is all process-local except temporary descriptor table entries owned by the process.

## Dependencies and Integration Points

It requires x86_64, signal handling, pthread/futex support, `modify_ldt` or `set_thread_area`, ptrace, and optional FSGSBASE CPU/kernel enablement. It integrates with kernel context-switch and ptrace register save/restore paths.

## Risks and Edge Cases

The test intentionally loads unusual selectors and bases, including `0xffffffffffffffff`, and relies on signal faults to infer bases. It pins to CPU 0 and assumes affinity succeeds. Behavior differs between older/newer kernels and AMD behavior around null selectors; the test accounts for some historical differences but can still expose platform-specific behavior.

## Test Signals

Pass signals are matching `ARCH_GET_GS` and fault-inferred bases, preserved GS selector/base across helper-thread scheduling, zero GSBASE after unexpected remote manipulation, successful `wrgsbase()` preservation when enabled, and expected ptrace selector/base behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/fsgsbase.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/fsgsbase_restore.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/fsgsbase_restore.c

## Purpose

`fsgsbase_restore.c` simulates a debugger redirecting a tracee into a function and then restoring saved registers with `PTRACE_SETREGS`. It verifies that FS/GS segment selector and base state is restored correctly even if the injected function modifies the segment register.

## Important APIs, Types, and Functions

The test uses `modify_ldt`, 32-bit `set_thread_area` fallback via `int $0x80`, `ptrace(PTRACE_TRACEME/GETREGS/SETREGS/CONT/DETACH)`, `tgkill(SIGSTOP)`, and helper `dereference_seg_base()` from `clang_helpers_32.S` or `clang_helpers_64.S`. `SEG` is `%gs` on x86_64 and `%fs` on i386. Important local functions are `init_seg()` and `tracee_zap_segment()`.

## Control Flow

`main()` maps a low target word containing `EXPECTED_VALUE`, installs a segment descriptor pointing at it, and verifies `dereference_seg_base()` reads the value. The child tracee stops under ptrace, later resumes and re-checks the segment. The parent saves registers, changes the tracee IP to `tracee_zap_segment()`, resumes it, waits for the function to set the segment register to a nonzero selector with base zero and stop again, restores the original register set, detaches, and checks that the tracee exits successfully after reading the expected value again.

## State and Persistence Behavior

State is confined to the process pair: low mapped memory, descriptor entries, tracee registers, and ptrace stop states. There is no persistence.

## Dependencies and Integration Points

It depends on segment descriptor support through `modify_ldt` or `set_thread_area`, ptrace register APIs, architecture-specific user register layouts, and assembly helpers for clang-compatible segment dereference.

## Risks and Edge Cases

If neither descriptor API works, the test prints a note and exits without meaningful coverage. Segment behavior differs across architectures and older CPUs, especially around null selectors, so the injected function uses a nonzero selector to avoid defeating the test. Ptrace errors abort through `err()`.

## Test Signals

Pass signals are initial and post-restore segment reads matching `EXPECTED_VALUE`, successful tracee stop/resume/detach sequencing, and final `[OK] All is well.`
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/fsgsbase_restore.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/helpers.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/helpers.h

## Purpose

`helpers.h` provides small shared helpers for x86 selftests: reading/writing EFLAGS and installing/removing SA_SIGINFO signal handlers with kselftest failure semantics.

## Important APIs, Types, and Functions

`get_eflags()` uses `__builtin_ia32_readeflags_u64()` or `_u32()`. `set_eflags()` uses `__builtin_ia32_writeeflags_u64()` or `_u32()`. `sethandler()` wraps `sigaction()` with `SA_SIGINFO | flags`, and `clearhandler()` restores `SIG_DFL`. Both fail with `ksft_exit_fail_msg()` on `sigaction` errors.

## Control Flow

Consumers include this header and call inline helpers directly. Signal helper setup zeroes `struct sigaction`, sets the callback/mask/flags, and installs it.

## State and Persistence Behavior

It mutates only the current process flags register or signal dispositions. There is no persistence.

## Dependencies and Integration Points

It depends on x86 compiler builtins, `<asm/processor-flags.h>`, POSIX signals, and `kselftest.h`.

## Risks and Edge Cases

Signal handlers installed through `sethandler()` always use `SA_SIGINFO`; callers needing a simple handler must adapt. Failure exits the test immediately, which is appropriate for setup helpers but not for optional signal paths.

## Test Signals

The helpers are validated indirectly by tests that depend on correct EFLAGS and signal-handler behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/ioperm.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/ioperm.c

## Purpose

`ioperm.c` tests Linux `ioperm(2)` I/O port bitmap behavior. It verifies default denial, enabling/disabling a port, fork inheritance and copy-on-write behavior, and privilege checks after dropping uid.

## Important APIs, Types, and Functions

The test uses `ioperm()`, inline `outb`, `sched_setaffinity()`, fork/wait, `setresuid()`, and SIGSEGV recovery through `sigsetjmp()`. Helpers are `try_outb()`, `expect_ok()`, and `expect_gp()`.

## Control Flow

`main()` pins to CPU 0, confirms writes to ports `0x80` and `0xed` fault by default, tries to enable port `0x80`, and exits successfully with an informational message if permission is unavailable. With permission, it verifies port `0x80` works and `0xed` faults, disables `0x80`, verifies both fault, re-enables `0x80`, forks a child to check inherited permission and child-local bitmap changes, confirms the parent still has `0x80`, drops uid to 1, verifies disabling still works unprivileged, and verifies enabling again fails unprivileged.

## State and Persistence Behavior

State is the process I/O permission bitmap, CPU affinity, and uid. There is no file persistence. The test writes to legacy I/O port `0x80` when permitted.

## Dependencies and Integration Points

It requires x86 I/O port instruction support and sufficient privilege for positive `ioperm()` coverage. It integrates with signal delivery for general-protection faults.

## Risks and Edge Cases

Running as non-root reduces coverage but exits success after noting the skip-like condition. Port writes can have platform-specific side effects, though port `0x80` is traditionally used as a safe delay/debug port. `try_outb()` installs a reset-on-use SIGSEGV handler and does not clear it after successful paths because return occurs before `clearhandler()`.

## Test Signals

Pass signals are expected `[OK]` messages for faulting/default ports, working `0x80` after enable, failure after disable, child success with independent bitmap changes, and unprivileged enable failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/ioperm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/iopl.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/iopl.c

## Purpose

`iopl.c` tests x86 `iopl(2)` semantics, especially that IOPL level 3 does not let userspace actually disable interrupts with CLI/STI, that I/O bitmap state is preserved/restored, that IOPL behavior across fork is correct, and that privilege checks work after dropping uid.

## Important APIs, Types, and Functions

It uses `iopl()`, `ioperm()`, inline `outb`, `cli`, `sti`, `pushf/pop`, fork/wait, `setresuid()`, and SIGSEGV recovery. Helpers include `try_outb()`, `expect_ok_outb()`, `expect_gp_outb()`, `try_cli()`, `try_sti()`, `expect_gp_sti()`, and `test_cli()`.

## Control Flow

The test pins to CPU 0 and tries `iopl(3)`, exiting successfully with a note if unsupported or not privileged. With IOPL 3, it ensures CLI/STI fault or are NOP-emulated rather than disabling interrupts, and that `outb 0x80` works. It establishes an I/O bitmap, drops IOPL to 0, verifies bitmap still permits `0x80`, clears the bitmap, forks a child that sets IOPL 3 and writes `0x80`, then confirms the parent still cannot write. Finally it tests that unprivileged callers can keep/drop an already-held IOPL 3 but cannot raise from 0.

## State and Persistence Behavior

State is process-local IOPL, I/O bitmap, CPU affinity, and uid. No persistence exists. The test can write to I/O port `0x80`.

## Dependencies and Integration Points

It requires x86 IOPL support and privilege for full coverage. It targets kernel entry/return, Xen-like emulation, signal delivery, fork inheritance, and capability checks.

## Risks and Edge Cases

The code checks `case -ENOSYS` after `iopl(3)`, but libc returns `-1` with `errno`, so this branch is unlikely to trigger as intended. CLI/STI behavior can be fault or NOP-emulation, both accepted. Running unprivileged reduces coverage.

## Test Signals

Pass signals include blocked/NOPed CLI/STI, working port I/O only when expected, child success without contaminating parent, and correct unprivileged iopl transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/iopl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/lam.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/lam.c

## Purpose

`lam.c` tests x86 Linear Address Masking userspace behavior. It validates tagged pointers with malloc, mmap, syscalls, get_user paths, io_uring, fork/thread/exec inheritance, reported max tag bits, and optional PASID/SVA interactions with Intel DSA.

## Important APIs, Types, and Functions

It defines LAM arch prctls `ARCH_GET_UNTAG_MASK`, `ARCH_ENABLE_TAGGED_ADDR`, `ARCH_GET_MAX_TAG_BITS`, and `ARCH_FORCE_TAGGED_SVA`. Important helpers include `lam_is_available()`, `la57_enabled()`, `set_lam()`, `get_default_tag_bits()`, `get_lam()`, `set_metadata()`, `handle_lam_test()`, `handle_max_bits()`, `handle_malloc()`, `handle_mmap()`, `handle_syscall()`, `get_user_syscall()`, io_uring helpers `setup_io_uring()`, `mmap_io_uring()`, `handle_uring_sq()`, `handle_uring_cq()`, `do_uring()`, inheritance helpers `handle_execve()`, `handle_inheritance()`, `handle_thread()`, `handle_thread_enable()`, and PASID helpers `Dsa_Init_Sysfs()`, `allocate_dsa_pasid()`, `set_force_svm()`, and `handle_pasid()`.

## Control Flow

`main()` skips if CPUID or kernel prctl support says LAM is unavailable, parses `-t` to select a bitmask of test families, and returns current LAM mode when invoked with `-t 0x0` by the exec test. Each testcase is run in a forked child via `run_test()` so process LAM mode changes are isolated. The malloc, mmap, syscall, and io_uring cases enable LAM before or after allocation depending on `later`, tag pointers with bits 62:57, and expect success or SIGSEGV/error. `get_user_syscall()` uses `FIOASYNC` on a memfd to test properly tagged user pointers and malformed kernel/noncanonical pointers. Inheritance cases verify fork/thread inheritance, disallow child-thread enablement, and confirm exec disables LAM. PASID cases configure DSA sysfs and run LAM/PASID/SVA operations in several orderings.

## State and Persistence Behavior

State includes process LAM mode, mapped test pages, malloc buffers, io_uring rings, temporary memfd, cloned thread state, DSA sysfs configuration, and optional `/dev/dsa/wq0.1` mappings. No ordinary files are persisted by the test itself, but PASID setup writes to sysfs and binds devices.

## Dependencies and Integration Points

It requires x86_64, CPU LAM support, kernel `CONFIG_ADDRESS_MASKING`, arch prctl support, io_uring for that family, and optional idxd/DSA/SVA support with `intel_iommu=on,sm_on` for PASID. It integrates with kselftest plan/result APIs.

## Risks and Edge Cases

`run_test()` prints results before `ksft_set_plan()`, which is unusual for TAP consumers. Several negative tests treat any nonzero errno path as expected. `get_user_syscall()` calls `munmap(ptr, PAGE_SIZE)` after `ptr` may have been modified with tag or kernel bits, which is risky if the pointer is no longer the original mapped address. PASID tests perform real sysfs device configuration and may disturb an existing DSA setup.

## Test Signals

Pass signals are kselftest results for each selected case: tagged malloc/mmap/syscall/io_uring success under LAM, expected failures without LAM or for kernel-like pointers, correct max tag bits, fork/thread inheritance behavior, exec reset to `LAM_NONE`, and expected PASID/SVA ordering outcomes or skips when DSA/SVA is unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/lam.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/ldt_gdt.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/ldt_gdt.c

## Purpose

`ldt_gdt.c` validates x86 LDT and GDT descriptor installation, validation, invalidation, fork/exec semantics, cross-CPU LDT invalidation, and segment register clearing when `set_thread_area` removes GDT entries.

## Important APIs, Types, and Functions

It uses `modify_ldt`, 32-bit `set_thread_area` via `int $0x80`, `struct user_desc`, `lsl`, `lar`, segment register loads, futexes, pthreads, CPU affinity, signals, fork/exec, and `arch_prctl` on x86_64 for FS/GS base restoration. Important helpers include `check_invalid_segment()`, `check_valid_segment()`, `install_valid_mode()`, `install_valid()`, `install_invalid()`, `safe_modify_ldt()`, `fail_install()`, `do_simple_tests()`, `threadproc()`, `fix_sa_restorer()`, `do_multicpu_tests()`, `finish_exec_test()`, `do_exec_test()`, `setup_counter_page()`, `invoke_set_thread_area()`, `setup_low_user_desc()`, and `test_gdt_invalidation()`.

## Control Flow

`main()` handles the exec-child mode by checking LDT entry 0 is invalid after exec. Normal execution maps a low counter page, tries to allocate a GDT entry with `set_thread_area`, runs descriptor installation tests for many code/data, present/not-present, page-limit, 16/32-bit, conforming, read-only, expand-down, usable, and long-mode combinations, checks invalid entries, tests fork inheritance of LDT entries, stress-installs up to 8192 LDT entries, verifies invalid high entry rejection, and tests deletion edge cases. It then runs cross-CPU invalidation by loading an LDT stack selector while a helper thread clears the LDT entry. It runs an exec test to ensure LDT is not inherited, and finally, if a GDT entry is available, tests that clearing it invalidates DS/ES/FS/GS and zeroes FS/GS bases as expected.

## State and Persistence Behavior

State is process-local descriptor table entries, segment registers, mapped low memory, thread/futex state, signal handlers, CPU affinity, and child process state. No files are persisted, but `/proc/self/exe` is execed for the exec inheritance test.

## Dependencies and Integration Points

It depends on x86 descriptor instructions, `modify_ldt` availability for full LDT coverage, `set_thread_area` for GDT coverage, 32-bit syscall ABI support for GDT tests, multiple CPUs for cross-CPU invalidation coverage, and signal behavior around invalid stack selectors.

## Risks and Edge Cases

Some kernels disable `modify_ldt`, causing skips for large portions. Cross-CPU invalidation requires CPU 0 and CPU 1 affinity; single-CPU systems skip it. The test deliberately loads SS/FS/GS with descriptors that may become invalid, relying on signal recovery. The glibc `sa_restorer` workaround is needed on i386 to avoid unrelated signal-frame failures.

## Test Signals

Pass signals include expected AR/limit values from LAR/LSL, invalid descriptors staying invalid, successful fork inheritance but exec cleanup, all cross-CPU invalidation iterations faulting safely, and DS/ES/FS/GS clearing plus FSBASE/GSBASE zeroing after GDT entry deletion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/ldt_gdt.c -->
