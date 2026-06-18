# subset-b-006324 samples research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/pktgen/pktgen_sample01_simple.sh -->
# sources/distributed-fs/ceph-client/samples/pktgen/pktgen_sample01_simple.sh

## Purpose

This shell sample configures Linux pktgen for a single transmit thread and one network device. It demonstrates the smallest useful pktgen setup: parse common parameters, require a destination MAC, default the destination IP, randomize UDP source ports, and start `/proc/net/pktgen/pgctrl`.

## Important APIs, Types, and Functions

The script depends on `functions.sh` for `root_check_run_with_sudo`, `trap_exit`, `pg_ctrl`, `pg_thread`, `pg_set`, address parsing, and validation. `parameters.sh` supplies `DEV`, `DEST_IP`, `DST_MAC`, `COUNT`, `PKT_SIZE`, `DELAY`, `APPEND`, `IP6`, `DST_PORT`, and `UDP_CSUM`. The local `print_result()` reads `/proc/net/pktgen/$DEV`.

## Control Flow

After privilege escalation and parameter parsing, defaults are filled, destination address and optional UDP destination port are parsed, and pktgen state is reset unless `APPEND` is set. Thread 0 is cleared and given `$DEV`; the device receives count, clone, packet size, delay, no timestamping, destination MAC/IP range, optional destination-port randomization, UDP checksum, and random UDP source port range. If not appending, it starts pktgen and prints device results.

## State and Persistence Behavior

State is external to the script and lives under `/proc/net/pktgen`: thread device membership and device generator attributes persist until reset or rewritten. `APPEND` intentionally avoids reset so multiple scripts can compose a run.

## Dependencies and Integration Points

It requires root, pktgen support loaded in the running kernel, a usable transmit interface, a valid neighbor/receiver MAC, and the companion pktgen helper scripts.

## Risks and Edge Cases

Missing `DST_MAC` is fatal. `COUNT=0` can run forever. `clone_skb` can defeat per-packet randomness. Bad IP/port values should be caught by helper validators, but invalid interface names or unavailable pktgen files fail at write time.

## Test Signals

Run with a test interface and `-m` destination MAC, then inspect `/proc/net/pktgen/$DEV`, packet counters, and receiver captures. `APPEND=1` should configure without starting.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/pktgen/pktgen_sample01_simple.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/pktgen/pktgen_sample02_multiqueue.sh -->
# sources/distributed-fs/ceph-client/samples/pktgen/pktgen_sample02_multiqueue.sh

## Purpose

This pktgen sample shows how to transmit from multiple pktgen kernel threads against one multiqueue device by using the `dev@thread` naming convention. It is intended for CPU-scaled transmit testing with one generator instance per selected CPU/thread.

## Important APIs, Types, and Functions

The script uses the common pktgen `functions.sh` and `parameters.sh` variables, especially `DEV`, `F_THREAD`, `L_THREAD`, and `THREADS`. It writes thread membership through `pg_thread` and generator attributes through `pg_set`. It uses `QUEUE_MAP_CPU`, `UDPSRC_RND`, optional `UDPDST_RND`, and optional `UDPCSUM`.

## Control Flow

The script defaults count, clone behavior, destination IP/MAC, and UDP source-port range, then resets pktgen unless in append mode. For every thread from `F_THREAD` to `L_THREAD`, it constructs `$DEV@$thread`, clears prior devices, adds that synthetic device to the pktgen thread, binds queue selection to CPU, and applies common packet attributes. The run phase starts pgctrl once and prints a short `Result:` block for every thread device.

## State and Persistence Behavior

Each `dev@thread` has independent pktgen device state, while the physical NIC and its queues are shared. The script rewrites thread membership unless `APPEND` is set. Runtime stats accumulate in `/proc/net/pktgen/$DEV@$thread` until reset.

## Dependencies and Integration Points

It integrates with NIC multiqueue queue selection and benefits from IRQ affinity mapping configured outside the script. It requires the pktgen procfs control plane and companion helper scripts.

## Risks and Edge Cases

Thread counts beyond available CPUs or queue count can generate misleading results. `QUEUE_MAP_CPU` only helps if queues and IRQs are aligned. Default destination MAC is only a placeholder and may black-hole traffic.

## Test Signals

Expected signals are one pktgen device per selected thread, nonzero per-thread result counters, and balanced NIC queue stats when CPU/IRQ/queue affinity is correctly configured.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/pktgen/pktgen_sample02_multiqueue.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/pktgen/pktgen_sample03_burst_single_flow.sh -->
# sources/distributed-fs/ceph-client/samples/pktgen/pktgen_sample03_burst_single_flow.sh

## Purpose

This sample targets maximum single-flow transmit performance. It intentionally avoids flow randomization and instead configures pktgen burst mode so drivers can use `skb->xmit_more` style batching to reduce hardware tail pointer updates.

## Important APIs, Types, and Functions

The script relies on `pg_ctrl`, `pg_thread`, and `pg_set` from `functions.sh`. Important pktgen attributes are `burst`, `QUEUE_MAP_CPU`, `count`, `clone_skb`, `pkt_size`, `delay`, `NO_TIMESTAMP`, `dst_mac`, `dst_min/max`, optional `udp_dst_min/max`, and optional `UDPCSUM`.

## Control Flow

After parsing shared parameters, it defaults `BURST=32`, `CLONE_SKB=0`, `COUNT=0`, destination IP, and destination MAC. It resets pktgen unless appending, then configures every requested thread as `$DEV@$thread`. Each configured generator maps queues to CPU, sets packet attributes, optional UDP destination-port randomization, and writes `burst $BURST` unless `BURST=0`. Non-append mode starts pktgen and prints each thread result.

## State and Persistence Behavior

All persistent state is pktgen procfs configuration. Because `COUNT` defaults to zero, the run persists until interrupted or pgctrl is stopped. The script does not save host tuning outside pktgen.

## Dependencies and Integration Points

It depends on kernel pktgen burst support, multiqueue NIC behavior, and the receiver's ability to handle a single UDP flow. It is a performance sample rather than a protocol correctness test.

## Risks and Edge Cases

Single-flow overload may pin one receiver CPU and hide aggregate NIC capacity. `BURST=0` disables the feature being demonstrated. Infinite count plus line-rate small packets can disrupt real networks.

## Test Signals

Useful signals are pktgen `Result:` pps/throughput output, NIC queue counters, receiver CPU saturation on one flow, and comparison of `BURST=0` versus the default burst value.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/pktgen/pktgen_sample03_burst_single_flow.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/pktgen/pktgen_sample04_many_flows.sh -->
# sources/distributed-fs/ceph-client/samples/pktgen/pktgen_sample04_many_flows.sh

## Purpose

This sample configures pktgen for many concurrent flows. It varies source IP addresses from the `198.18.0.0/15` benchmarking range and uses pktgen `flows`, `flowlen`, and `FLOW_SEQ` to model repeated packets per flow.

## Important APIs, Types, and Functions

Key helper APIs are the pktgen shell wrappers from `functions.sh`. Pktgen attributes include `IPSRC_RND`, `src_min`, `src_max`, `flows`, `flowlen`, `FLOW_SEQ`, `QUEUE_MAP_CPU`, common packet fields, optional `UDPDST_RND`, and optional `UDPCSUM`.

## Control Flow

After common setup, the script defaults destination parameters, `FLOWS=8000`, `FLOWLEN=10`, and rejects `BURST` because burst mode is not supported in this flow-generation mode. It parses the fixed source network, resets pktgen unless appending, configures each selected thread device, randomizes source IPs, sets the flow table size and packets-per-flow, then starts pgctrl and prints per-thread results unless in append mode.

## State and Persistence Behavior

Pktgen's in-kernel flow table and generator configuration hold the runtime state. `FLOW_SEQ` changes packet ordering so `FLOWLEN` packets are sent back-to-back from one flow before advancing. No repository or filesystem state is persisted beyond procfs configuration.

## Dependencies and Integration Points

It depends on pktgen flow support and the helper scripts. Receiver-side RSS, flow hashing, conntrack, routing, and application lookup caches are typical integration targets for the generated workload.

## Risks and Edge Cases

Large flow counts can stress receiver tables and test infrastructure. `FLOWS` is bounded by pktgen's maximum. Burst rejection is explicit, but invalid helper-derived thread ranges still fail through procfs writes.

## Test Signals

Validate via pktgen result output, packet captures showing many source IPs, receiver RSS distribution, and behavior changes when varying `FLOWS` and `FLOWLEN`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/pktgen/pktgen_sample04_many_flows.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/pktgen/pktgen_sample05_flow_per_thread.sh -->
# sources/distributed-fs/ceph-client/samples/pktgen/pktgen_sample05_flow_per_thread.sh

## Purpose

This sample creates one deterministic UDP/IP flow per pktgen thread. It is designed to test receiver-side scalability by giving each transmit CPU a distinct fixed source IP while sharing one destination.

## Important APIs, Types, and Functions

It uses common pktgen helper functions and variables from `parameters.sh`. Important pktgen controls include `QUEUE_MAP_CPU`, fixed `src_min/src_max`, `burst`, common packet attributes, optional destination-port randomization, and optional UDP checksum.

## Control Flow

The script defaults destination IP/MAC, `CLONE_SKB=0`, `BURST=32`, and infinite count. For each configured thread, it creates `$DEV@$thread`, maps queue-to-CPU, sets common packet fields, assigns a fixed source address `198.18.$((thread+1)).1`, and enables burst unless `BURST=0`. It starts all configured threads through pgctrl unless appending.

## State and Persistence Behavior

The meaningful state is per-thread pktgen configuration. Each thread has a stable source address based on thread id, making receiver flow placement repeatable across runs as long as thread selection is unchanged.

## Dependencies and Integration Points

It integrates with receiver RSS/flow steering and sender multiqueue behavior. It needs pktgen procfs, helper scripts, root privileges, and a valid destination MAC.

## Risks and Edge Cases

The source IP formula assumes thread ids fit into the third octet range. If thread ids are high, generated IPs can be invalid. Infinite count and burst mode can saturate network equipment.

## Test Signals

Capture traffic to confirm one source IP per thread, check per-thread pktgen results, and inspect receiver queue/CPU distribution.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/pktgen/pktgen_sample05_flow_per_thread.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/pktgen/pktgen_sample06_numa_awared_queue_irq_affinity.sh -->
# sources/distributed-fs/ceph-client/samples/pktgen/pktgen_sample06_numa_awared_queue_irq_affinity.sh

## Purpose

This sample extends multiqueue pktgen setup with NUMA-aware CPU selection and IRQ affinity. It binds selected NIC queue IRQs to CPUs on the NIC's NUMA node and maps each pktgen device to a specific queue.

## Important APIs, Types, and Functions

Besides the common pktgen helper calls, it uses helper functions `get_iface_node`, `get_iface_irqs`, and `get_node_cpus`. It writes `/proc/irq/<irq>/smp_affinity_list`, configures `queue_map_min/max`, and sets `QUEUE_MAP_CPU`, UDP source-port randomization, and common packet attributes.

## Control Flow

The script discovers the interface NUMA node, IRQ list, and node CPU list, then rejects thread counts exceeding IRQ or CPU capacity. For each thread index it picks `cpu_array[i + F_THREAD]`, names the pktgen device `$DEV@$thread`, writes the corresponding IRQ affinity, adds the device to that pktgen thread, pins the pktgen queue number to `i`, applies packet fields, and runs pgctrl unless appending.

## State and Persistence Behavior

Unlike earlier samples, this script changes persistent host IRQ affinity in `/proc/irq`. Pktgen state is also persistent until reset. The script does not restore old IRQ masks on exit.

## Dependencies and Integration Points

It integrates directly with NIC queue IRQs, NUMA topology, and pktgen queue mapping. It requires root and helper support for sysfs/procfs topology discovery.

## Risks and Edge Cases

The IRQ affinity changes can affect unrelated traffic after the sample ends. Thread offset handling can index beyond `cpu_array` if helper bounds differ. Not all devices expose per-queue IRQs in the expected format.

## Test Signals

Check `/proc/irq/*/smp_affinity_list`, pktgen per-device results, `ethtool -S` queue counters, and NUMA-local CPU utilization.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/pktgen/pktgen_sample06_numa_awared_queue_irq_affinity.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/qmi/Makefile -->
# sources/distributed-fs/ceph-client/samples/qmi/Makefile

## Purpose

This Kbuild fragment builds the QMI sample client module when `CONFIG_SAMPLE_QMI_CLIENT` is enabled.

## Important APIs, Types, and Functions

It uses the standard `obj-$(CONFIG_...) += object.o` Kbuild pattern and maps `qmi_sample_client.c` to `qmi_sample_client.o`.

## Control Flow

There is no runtime control flow. During kernel build, Kbuild evaluates `CONFIG_SAMPLE_QMI_CLIENT`; `y` links the object built-in and `m` builds a module.

## State and Persistence Behavior

It does not persist runtime state. Its only effect is build graph inclusion.

## Dependencies and Integration Points

The symbol must be defined by surrounding Kconfig. The C file depends on QRTR/QMI, platform devices, and debugfs.

## Risks and Edge Cases

Build failures surface if QMI dependencies are not selected by Kconfig or if the object name and source file diverge.

## Test Signals

Enable the config, build `samples/qmi/`, and confirm `qmi_sample_client.o` or `.ko` is produced.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/qmi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/qmi/qmi_sample_client.c -->
# sources/distributed-fs/ceph-client/samples/qmi/qmi_sample_client.c

## Purpose

This kernel module is a sample Qualcomm QMI client over QRTR. It discovers the test QMI service, creates one platform device per discovered server, connects a QMI handle to the remote port, and exposes debugfs files that send ping and data transactions.

## Important APIs, Types, and Functions

The file defines QMI TLV structures and `qmi_elem_info` arrays for name, ping request/response, and data request/response messages. `ping_write()` uses a custom response callback path with `qmi_txn_init`, `qmi_send_request`, and `qmi_txn_wait`; `ping_pong_cb()` validates the pong response. `data_write()` allocates request/response buffers, copies user data, sends a data request, and verifies the echoed response decoded by QMI helpers. Driver lifecycle is handled by `qmi_sample_probe()`, `qmi_sample_remove()`, `qmi_sample_new_server()`, `qmi_sample_del_server()`, `qmi_sample_init()`, and `qmi_sample_exit()`.

## Control Flow

Module init creates `/sys/kernel/debug/qmi_sample`, registers a platform driver, initializes `lookup_client`, and calls `qmi_add_lookup()` for `QMI_SERVICE_ID_TEST`. When a server appears, QMI lookup allocates a platform device with a `sockaddr_qrtr` as platform data. Probe initializes a QMI handle, connects its socket, creates a per-server debugfs directory named `node:port`, and installs `data` and `ping` files. Writes to those files synchronously issue QMI transactions and return either bytes accepted or an errno.

## State and Persistence Behavior

Global state is `lookup_client` and `qmi_debug_dir`. Per-server state is `struct qmi_sample`, containing a QMI handle and debugfs dentries. Remote service association persists through the platform device until lookup deletion or module unload. No data is stored beyond in-flight transactions.

## Dependencies and Integration Points

It depends on debugfs, platform bus, QRTR sockets, `linux/soc/qcom/qmi.h`, and a remote QMI test service. It integrates with QMI service discovery through `qmi_ops`.

## Risks and Edge Cases

Debugfs creation errors unwind manually. `qmi_sample_handlers` uses `decoded_size = sizeof(struct test_ping_req_msg_v01)` for a response handler, which is suspicious and worth build/runtime scrutiny. Data writes allocate large request/response objects and truncate input to 8192 bytes. Transaction timeouts return errors after five seconds.

## Test Signals

Load the module on a system with QRTR test service, observe debugfs directories, write to `ping` and `data`, and check dmesg for response validation errors. Build coverage should include QMI and debugfs enabled.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/qmi/qmi_sample_client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/rpmsg/Makefile -->
# sources/distributed-fs/ceph-client/samples/rpmsg/Makefile

## Purpose

This Kbuild fragment builds the rpmsg sample client when `CONFIG_SAMPLE_RPMSG_CLIENT` is enabled.

## Important APIs, Types, and Functions

It uses `obj-$(CONFIG_SAMPLE_RPMSG_CLIENT) += rpmsg_client_sample.o`.

## Control Flow

Kbuild includes the object as built-in or module depending on the config value. There is no runtime logic in the Makefile.

## State and Persistence Behavior

Only build state is affected.

## Dependencies and Integration Points

The referenced C file integrates with the rpmsg bus and remote processor channels.

## Risks and Edge Cases

The Makefile assumes Kconfig handles rpmsg dependencies; otherwise compile or link errors occur.

## Test Signals

Enable the config and verify the sample object/module builds.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/rpmsg/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/rpmsg/rpmsg_client_sample.c -->
# sources/distributed-fs/ceph-client/samples/rpmsg/rpmsg_client_sample.c

## Purpose

This module is a minimal rpmsg client driver. It binds to channels named `rpmsg-client-sample`, sends an initial message to the remote processor, and replies to each received message until a configurable receive count is reached.

## Important APIs, Types, and Functions

The driver defines module parameter `count`, per-instance `struct instance_data { int rx_count; }`, `rpmsg_sample_probe()`, `rpmsg_sample_cb()`, and `rpmsg_sample_remove()`. It uses `rpmsg_send()`, `devm_kzalloc()`, `dev_set_drvdata()`, `dev_get_drvdata()`, `print_hex_dump_debug()`, and `module_rpmsg_driver()`.

## Control Flow

Probe logs the channel source/destination, allocates instance data, stores it on the rpmsg device, and sends `"hello world!"`. The callback increments `rx_count`, hex-dumps the payload at debug level, stops replying once the count threshold is reached, otherwise sends another hello message. Remove only logs device removal.

## State and Persistence Behavior

Persistent state is per-bound-device `rx_count`; it is devm-managed and tied to the rpmsg device lifecycle. The module parameter `count` is writable through sysfs mode `0644` and controls future callback behavior.

## Dependencies and Integration Points

It depends on the rpmsg framework, a remote processor endpoint publishing the matching channel, and transport-specific endpoint creation.

## Risks and Edge Cases

If the remote side echoes immediately, this forms a ping-pong loop until `count`. Send failures are logged but do not unregister the driver. `count <= 0` effectively disables reply after the first receive because `rx_count >= count`.

## Test Signals

Bind against a remoteproc sample service, check dmesg for probe and incoming message logs, verify the receive count stops replies, and inspect dynamic debug output for payload dumps.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/rpmsg/rpmsg_client_sample.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/rust/Kconfig -->
# sources/distributed-fs/ceph-client/samples/rust/Kconfig

## Purpose

This Kconfig file defines the top-level Rust samples menu and individual build options for Rust kernel sample modules and host programs.

## Important APIs, Types, and Functions

It uses `menuconfig SAMPLES_RUST`, gated by `depends on RUST`, then declares tristate sample symbols such as `SAMPLE_RUST_CONFIGFS`, `SAMPLE_RUST_MISC_DEVICE`, `SAMPLE_RUST_DMA`, bus driver samples, and `SAMPLE_RUST_HOSTPROGS`. Some entries express dependencies or selects, including `CONFIGFS_FS`, `DEBUG_FS`, `I2C=y`, `PCI`, `USB=y`, `AUXILIARY_BUS`, and `SOC_BUS`.

## Control Flow

Kconfig exposes child options only inside `if SAMPLES_RUST`. Selected symbols drive `samples/rust/Makefile`, which maps configs to object files.

## State and Persistence Behavior

The file persists only kernel configuration choices in `.config`. Runtime state belongs to the compiled sample modules.

## Dependencies and Integration Points

It integrates with the kernel Rust build infrastructure, Kbuild objects in this directory, and subsystem Kconfig symbols for configfs, debugfs, PCI, I2C, USB, auxiliary bus, and SoC bus.

## Risks and Edge Cases

Dependencies such as `I2C=y` and `USB = y` intentionally require built-in core support; module-only subsystem configurations may hide samples. Missing or renamed source files will surface in Kbuild.

## Test Signals

Run menuconfig or `scripts/config` to enable samples, build `samples/rust`, and confirm expected `.o` or `.ko` artifacts are produced.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/rust/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/rust/Makefile -->
# sources/distributed-fs/ceph-client/samples/rust/Makefile

## Purpose

This Kbuild file maps Rust sample Kconfig symbols to kernel objects and configures one C/Rust mixed sample for trace events.

## Important APIs, Types, and Functions

It adds `ccflags-y += -I$(src)` for trace event headers, lists `obj-$(CONFIG_SAMPLE_RUST_...) += ...o`, defines `rust_print-y := rust_print_main.o rust_print_events.o`, and descends into `hostprogs` when `CONFIG_SAMPLE_RUST_HOSTPROGS` is enabled.

## Control Flow

During build, Kbuild evaluates each config symbol. Most entries compile a single `.rs` object. `rust_print.o` is a composite built from Rust main code plus C tracepoint definition code.

## State and Persistence Behavior

It has no runtime state. Its persistent effect is build dependency shape.

## Dependencies and Integration Points

It integrates with Rust-for-Linux Kbuild support, C tracepoint include rules, and the Kconfig file in the same folder.

## Risks and Edge Cases

The trace include path is required for generated trace headers; removing it can break `rust_print_events.c`. Composite object naming must match the module name selected by Kconfig.

## Test Signals

Build all enabled Rust samples and verify each configured module object appears; specifically check that `rust_print` links both Rust and C objects.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/rust/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/rust/hostprogs/Makefile -->
# sources/distributed-fs/ceph-client/samples/rust/hostprogs/Makefile

## Purpose

This Kbuild fragment builds the Rust host program sample named `single`.

## Important APIs, Types, and Functions

It uses `hostprogs-always-y := single` and marks `single-rust := y`, telling Kbuild the host tool is implemented in Rust.

## Control Flow

When the parent Makefile descends into this directory, Kbuild builds the `single` host program and its Rust modules.

## State and Persistence Behavior

Only build artifacts are produced; no kernel runtime state is involved.

## Dependencies and Integration Points

It relies on kernel hostprog Rust support and the `single.rs`, `a.rs`, and `b.rs` files in this directory.

## Risks and Edge Cases

Host Rust compiler availability and Kbuild's module discovery are the main risks.

## Test Signals

Enable `SAMPLE_RUST_HOSTPROGS` and build; the `single` host binary should be produced and print the expected messages when run.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/rust/hostprogs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/rust/hostprogs/a.rs -->
# sources/distributed-fs/ceph-client/samples/rust/hostprogs/a.rs

## Purpose

This is a tiny Rust host-program module used by `single.rs` to demonstrate splitting a host Rust binary into modules.

## Important APIs, Types, and Functions

It exports `pub(crate) fn f(x: i32)`, which prints `The number is {x}.` with Rust's standard `println!` macro.

## Control Flow

There is no independent entry point. `single.rs` imports module `a` and calls `a::f(b::CONSTANT)`.

## State and Persistence Behavior

The function is stateless and persists nothing.

## Dependencies and Integration Points

It depends on the Rust standard library available to host programs, not kernel Rust APIs.

## Risks and Edge Cases

No material runtime risk; build risk is module path discovery from `single.rs`.

## Test Signals

Running the built `single` binary should include `The number is 42.`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/rust/hostprogs/a.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/rust/hostprogs/b.rs -->
# sources/distributed-fs/ceph-client/samples/rust/hostprogs/b.rs

## Purpose

This Rust host-program module provides a constant consumed by `single.rs`.

## Important APIs, Types, and Functions

It declares `pub(crate) const CONSTANT: i32 = 42`.

## Control Flow

There is no control flow. The constant is read by `single.rs` and passed to `a::f()`.

## State and Persistence Behavior

The constant is compile-time data with no persistence side effects.

## Dependencies and Integration Points

It integrates with the Rust module system through `mod b;` in `single.rs`.

## Risks and Edge Cases

Changing the constant only changes host-program output; type changes would require updating callers.

## Test Signals

The built host program should print `The number is 42.`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/rust/hostprogs/b.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/rust/hostprogs/single.rs -->
# sources/distributed-fs/ceph-client/samples/rust/hostprogs/single.rs

## Purpose

This is the entry point for the Rust host-program sample. It demonstrates a Kbuild-built Rust host binary using sibling modules.

## Important APIs, Types, and Functions

The file declares `mod a;` and `mod b;`, then defines `fn main()` using `println!`, `a::f`, and `b::CONSTANT`.

## Control Flow

`main()` prints `Hello world!` and then calls `a::f(42)` through the constant imported from module `b`.

## State and Persistence Behavior

The host program has no durable state and exits immediately after printing.

## Dependencies and Integration Points

It integrates with `hostprogs/Makefile` through `single-rust := y` and uses standard Rust host facilities rather than kernel APIs.

## Risks and Edge Cases

The sample is intentionally simple; risk is limited to Rust hostprog build support.

## Test Signals

Run the resulting `single` binary and verify it prints both the greeting and number line.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/rust/hostprogs/single.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/rust/rust_configfs.rs -->
# sources/distributed-fs/ceph-client/samples/rust/rust_configfs.rs

## Purpose

This Rust kernel module demonstrates configfs subsystem, group, child-group, and attribute support. It creates a `rust_configfs` subsystem with readable and writable attributes and dynamic nested groups.

## Important APIs, Types, and Functions

The module uses `module!`, `kernel::InPlaceModule`, `configfs::Subsystem`, `configfs::Group`, `configfs_attrs!`, `GroupOperations`, and indexed `AttributeOperations`. `Configuration` stores a static `message` and a mutex-protected page-sized `bar` buffer. `Child` and `GrandChild` implement nested group behavior with `baz` and `gc` attributes.

## Control Flow

Module init constructs a configfs item type for `Configuration`, registers the subsystem, and provides `Configuration::make_group()` for user-created child directories. Attribute `message` reads a fixed string. Attribute `bar` reads/writes the mutex-protected buffer. Child group creation returns `Group<GrandChild>`, and child/grandchild attributes return fixed strings.

## State and Persistence Behavior

Persistent state exists only while the module is loaded and configfs items exist. `bar` stores the last written bytes and length under a `Mutex`. Dynamic groups are represented by pinned configfs objects and cleaned up through configfs lifetimes.

## Dependencies and Integration Points

It depends on `CONFIGFS_FS`, Rust pin-init support, kernel allocation APIs, mutexes, and `PAGE_SIZE` buffers. User space interacts through mounted configfs.

## Risks and Edge Cases

`bar.store()` copies `page.len()` bytes into a page-sized buffer; it relies on configfs store size guarantees. Group names are converted with `try_into()` and can fail. Locking is simple but must protect length and buffer coherently.

## Test Signals

Load the module, mount configfs, inspect `rust_configfs/message`, write/read `bar`, create child and grandchild directories, and read `baz`/`gc`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/rust/rust_configfs.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/rust/rust_debugfs.rs -->
# sources/distributed-fs/ceph-client/samples/rust/rust_debugfs.rs

## Purpose

This Rust platform driver sample demonstrates debugfs file creation for scalar, structured, and binary state attached to a firmware-described platform device.

## Important APIs, Types, and Functions

It uses `kernel::module_platform_driver!`, ACPI matching, `debugfs::Dir`, typed `debugfs::File`, `Atomic<usize>`, `Mutex<Inner>`, `CString`, `KVec`, and firmware node property access. `Inner` implements `FromStr` so debugfs can parse writes to the pair file.

## Control Flow

The ACPI table matches `LNUXBEEF`. Probe calls `RustDebugFs::new()`, which creates `sample_debugfs`, reads the device `compatible` property into a read-only file, and creates read/write files for `counter`, `pair`, `array_blob`, and `vector_blob`. A `pin_chain` post-initialization step sets counter to 91 and mutates the `Inner` pair.

## State and Persistence Behavior

State is held in the driver instance: an `ARef` to the platform device, the debugfs directory RAII object, file handles, an atomic counter, mutex-protected pair, fixed array blob, and vector blob. Debugfs entries are removed when the instance is dropped.

## Dependencies and Integration Points

It depends on `DEBUG_FS`, platform bus, ACPI firmware nodes, and Rust debugfs wrappers. User space uses debugfs files to inspect and modify state.

## Risks and Edge Cases

Probe requires a firmware node and `compatible` property; missing properties fail via `required_by(dev)`. `Inner::from_str` rejects malformed or extra tokens. Debugfs is for diagnostics and should not be treated as stable ABI.

## Test Signals

Boot with a matching ACPI SSDT, load the module, inspect debugfs files, write valid and invalid `pair` values, and verify counter/blob read/write behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/rust/rust_debugfs.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/rust/rust_debugfs_scoped.rs -->
# sources/distributed-fs/ceph-client/samples/rust/rust_debugfs_scoped.rs

## Purpose

This Rust module demonstrates scoped debugfs lifetimes. It creates a control directory with write-only callbacks that dynamically create and remove per-device debugfs subdirectories.

## Important APIs, Types, and Functions

It uses `debugfs::Dir`, `debugfs::Scope`, callback files, `KBox::pin_init`, `KVec`, `Atomic<usize>`, `Mutex`, `CString`, and `UserSliceReader`. `ModuleData` stores the base dynamic directory and a vector of pinned device scopes. `DeviceData` stores a name, atomic numeric files, and a binary blob.

## Control Flow

Module init creates `rust_scoped_debugfs`, a `dynamic` subdir, and a `control` scope. Writing `control/create` parses a name plus numeric values, creates a scoped directory under `dynamic`, adds one read/write file per numeric value plus a `blob`, and stores the scope in `devices`. Writing `control/remove` reads a name and retains only devices whose name differs.

## State and Persistence Behavior

Dynamic state is the `devices` vector under a mutex. Each element owns a scope; removing it from the vector drops the scope and removes that subtree. Numeric files hold atomic values, and the blob is a pinned mutex-protected 4 KiB array.

## Dependencies and Integration Points

It depends on Rust debugfs scope APIs, allocation, mutexes, and debugfs being enabled.

## Risks and Edge Cases

Input parsing caps names at 127 bytes and rejects invalid UTF-8 or numeric tokens. A failure while creating per-index filenames silently returns from the scope builder, so partial directories may be possible. Debugfs callbacks run in kernel context and must avoid unbounded allocation from hostile input.

## Test Signals

Load the module, write commands such as `dev0 1 2 3` to `control/create`, inspect `dynamic/dev0/`, mutate numeric files/blob, then remove by writing `dev0` to `control/remove`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/rust/rust_debugfs_scoped.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/rust/rust_dma.rs -->
# sources/distributed-fs/ceph-client/samples/rust/rust_dma.rs

## Purpose

This Rust PCI driver sample demonstrates DMA mask setup, coherent DMA allocation, typed DMA reads/writes, scatter-gather table construction, and cleanup-time verification against QEMU's `pci-testdev`.

## Important APIs, Types, and Functions

It implements `pci::Driver` for `DmaSampleDriver`, uses `pci_device_table!`, `Coherent<[MyStruct]>`, `dma_write!`, `dma_read!`, `DmaMask::new::<64>()`, `SGTable<Owned<VVec<u8>>>`, and `PinnedDrop`. `MyStruct` is marked `AsBytes` and `FromBytes`.

## Control Flow

Probe sets a 64-bit DMA mask, allocates a coherent slice sized for `TEST_VALUES`, writes test pairs through DMA access macros, allocates a virtual vector for a 4-page scatterlist, and stores all resources in the driver. On pinned drop, it checks coherent memory values and logs DMA addresses of SG entries.

## State and Persistence Behavior

Driver state holds an `ARef` to the PCI device, coherent allocation, and pinned SG table. Coherent data persists for the device lifetime. Drop asserts that the coherent values remain intact.

## Dependencies and Integration Points

It depends on PCI, QEMU `pci-testdev` vendor/device ID, kernel DMA API, scatterlist wrappers, and Rust pin-init.

## Risks and Edge Cases

The comment says DMA allocation/mapping calls are not concurrent before using unsafe `dma_set_mask_and_coherent`. Drop uses assertions; unexpected corruption can trigger kernel assertion behavior in a sample. The SG table is created for `ToDevice` without actual device DMA.

## Test Signals

Run under QEMU with `-device pci-testdev`, load the module, confirm probe/unload logs, coherent value assertions, and printed SG DMA addresses.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/rust/rust_dma.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/rust/rust_driver_auxiliary.rs -->
# sources/distributed-fs/ceph-client/samples/rust/rust_driver_auxiliary.rs

## Purpose

This sample demonstrates cooperation between a parent PCI driver and an auxiliary bus driver in Rust. The PCI driver registers two auxiliary devices, and the auxiliary driver connects back to the bound parent.

## Important APIs, Types, and Functions

It uses `auxiliary_device_table!`, `pci_device_table!`, `driver::Registration`, `auxiliary::Registration`, `Devres`, `pci::Driver`, `auxiliary::Driver`, and `TypeId` as sample private data. `ParentDriver::connect()` converts the auxiliary parent to a bound PCI device and reads parent driver data.

## Control Flow

Module init registers both PCI and auxiliary adapters. When QEMU `pci-testdev` probes, `ParentDriver` creates two devres-managed auxiliary registrations named `auxiliary` with ids 0 and 1. The auxiliary driver's probe logs the auxiliary id and calls `ParentDriver::connect()` to inspect the parent PCI IDs and private state.

## State and Persistence Behavior

Parent state includes a `TypeId` and two devres auxiliary registrations. Auxiliary driver instances are zero-sized. Device registrations are devres-bound to the parent lifetime.

## Dependencies and Integration Points

It depends on PCI, auxiliary bus support, and the REDHAT `pci-testdev` ID. It integrates two driver registrations in one module.

## Risks and Edge Cases

Driver registration order matters for matching. The connect path assumes the parent is a bound PCI device with `ParentDriver` data; type conversion or drvdata lookup failures abort auxiliary probe.

## Test Signals

Run with `pci-testdev`, enable auxiliary bus, load the module, and check logs for both auxiliary ids and parent PCI vendor/device data.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/rust/rust_driver_auxiliary.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/rust/rust_driver_faux.rs -->
# sources/distributed-fs/ceph-client/samples/rust/rust_driver_faux.rs

## Purpose

This minimal Rust module demonstrates creation of a faux device through the Rust faux-device abstraction.

## Important APIs, Types, and Functions

It uses `module!`, `kernel::Module`, `faux::Registration::new()`, `pr_info!`, and `dev_info!`. `SampleModule` stores the registration so the device remains registered until module drop.

## Control Flow

Module init logs startup, registers a faux device named `rust-faux-sample-device`, logs through the device, and returns the module state.

## State and Persistence Behavior

The only persistent state is `_reg: faux::Registration`, whose lifetime controls device registration. No user data is stored.

## Dependencies and Integration Points

It depends on the kernel faux device support exposed to Rust. It is intended as a registration/lifetime sample rather than a functional driver.

## Risks and Edge Cases

Failure to register returns an error from module init. Because the module name string is `rust_faux_driver` while the Kconfig help says `rust_driver_faux`, packaging should be checked in builds.

## Test Signals

Load the module and verify the init and device log messages; unload should unregister the faux device through RAII.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/rust/rust_driver_faux.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/rust/rust_driver_i2c.rs -->
# sources/distributed-fs/ceph-client/samples/rust/rust_driver_i2c.rs

## Purpose

This Rust sample is a basic I2C client driver with OF, ACPI, and traditional I2C id-table matching.

## Important APIs, Types, and Functions

It uses `acpi_device_table!`, `i2c_device_table!`, `of_device_table!`, implements `i2c::Driver` for `SampleDriver`, and registers via `module_i2c_driver!`. The callbacks are `probe()`, `shutdown()`, and `unbind()`.

## Control Flow

Matching can occur through ACPI HID `LNUXBEEF`, I2C name `rust_driver_i2c`, or OF compatible `test,rust_driver_i2c`. Probe logs the device and optional id info, returns a zero-sized driver instance, and later shutdown/unbind log lifecycle events.

## State and Persistence Behavior

The driver instance carries no private state. Device lifecycle state is managed by the I2C core.

## Dependencies and Integration Points

It depends on built-in I2C core support (`I2C=y`) and integrates with the three firmware/device-id matching paths.

## Risks and Edge Cases

Because it is stateless, it does not validate adapter functionality or communicate with hardware. It is useful for binding/lifecycle tests, not device protocol tests.

## Test Signals

Instantiate a matching I2C client, load the module, and verify probe, shutdown, and unbind logs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/rust/rust_driver_i2c.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/rust/rust_driver_pci.rs -->
# sources/distributed-fs/ceph-client/samples/rust/rust_driver_pci.rs

## Purpose

This Rust PCI driver sample demonstrates typed MMIO register access, PCI config-space reads, BAR mapping with devres, and cleanup behavior using QEMU's `pci-testdev`.

## Important APIs, Types, and Functions

It uses `register!` to define MMIO and config registers, `pci_device_table!`, `pci::Bar`, `Devres`, `ARef<pci::Device>`, and `PinnedDrop`. `SampleDriver::testdev()` selects a test index, reads offset/data registers, writes data back to the offset, and reads a count. `config_space()` demonstrates typed reads from PCI config space.

## Control Flow

Probe enables memory decoding, sets bus mastering, maps BAR0 sized to the sample register block, accesses the BAR, runs the `pci-testdev` data-match test, logs config-space fields, and stores the mapped BAR and index. `unbind()` resets the testdev by writing the saved index. Drop logs removal.

## State and Persistence Behavior

State includes the PCI device reference, devres BAR mapping, and selected test index. Hardware-side test count and config registers are external state on the emulated PCI device.

## Dependencies and Integration Points

It depends on PCI support, QEMU `pci-testdev`, Rust IO register abstractions, and the REDHAT vendor/device ID.

## Risks and Edge Cases

`try_write8` protects dynamic offsets, but invalid testdev behavior can still return errors. The sample assumes BAR0 layout exactly matches QEMU `pci-testdev`.

## Test Signals

Run QEMU with `-device pci-testdev`, load the module, and check logs for data-match count, vendor/revision/BAR reads, and removal.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/rust/rust_driver_pci.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/rust/rust_driver_platform.rs -->
# sources/distributed-fs/ceph-client/samples/rust/rust_driver_platform.rs

## Purpose

This Rust platform driver sample demonstrates OF and ACPI matching plus firmware-node property parsing from Rust.

## Important APIs, Types, and Functions

It uses `of_device_table!`, `acpi_device_table!`, `platform::Driver`, `module_platform_driver!`, `ARef<platform::Device>`, `CString`, `property_read`, `property_read_bool`, `property_present`, `property_count_elem`, `property_read_array_vec`, and `property_get_reference_args`.

## Control Flow

Probe logs the matched id info, checks whether the firmware node is an OF node, and then calls `properties_parse()`. That helper matches compatible strings, reads required and optional scalar/string properties, checks booleans and presence, reads fixed and vector arrays, iterates children, and resolves reference arguments.

## State and Persistence Behavior

The driver stores only an `ARef` to the platform device. Parsed properties are logged and not cached. Drop logs removal.

## Dependencies and Integration Points

It integrates with platform bus, OF and ACPI match tables, firmware node property APIs, and QEMU ACPI SSDT testing described in comments.

## Risks and Edge Cases

Missing required OF properties cause probe failure for OF-backed devices. The sample intentionally discards one missing-property error to demonstrate diagnostic behavior. ACPI-matched devices skip OF-only parsing.

## Test Signals

Create a matching OF node or ACPI SSDT, load the module, and inspect dmesg for property parsing logs and probe info values.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/rust/rust_driver_platform.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/rust/rust_driver_usb.rs -->
# sources/distributed-fs/ceph-client/samples/rust/rust_driver_usb.rs

## Purpose

This Rust sample demonstrates a minimal USB interface driver with id-table matching, probe, and disconnect callbacks.

## Important APIs, Types, and Functions

It uses `usb_device_table!`, implements `usb::Driver` for `SampleDriver`, holds `ARef<usb::Interface>`, and registers via `module_usb_driver!`. The id table matches vendor `0x1234`, product `0x5678`.

## Control Flow

When a matching USB interface binds, probe logs through the interface device and stores an interface reference. On disconnect, it logs that the sample disconnected.

## State and Persistence Behavior

State is the held interface reference. The driver performs no endpoint allocation or I/O.

## Dependencies and Integration Points

It depends on built-in USB support and Rust USB wrappers. Matching requires a device or gadget exposing the hard-coded VID/PID.

## Risks and Edge Cases

The sample is lifecycle-only and does not verify interface class, alternate settings, or endpoints. The hard-coded VID/PID should not be used for real hardware without care.

## Test Signals

Attach or emulate a device with VID/PID `1234:5678`, load the module, and check probe/disconnect logs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/rust/rust_driver_usb.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/rust/rust_i2c_client.rs -->
# sources/distributed-fs/ceph-client/samples/rust/rust_i2c_client.rs

## Purpose

This Rust platform driver sample demonstrates manually registering a new I2C client from a parent platform device.

## Important APIs, Types, and Functions

It uses platform OF/ACPI match tables, `i2c::I2cAdapter::get`, `i2c::I2cBoardInfo`, `i2c::Registration`, `Devres`, `ARef<platform::Device>`, and `module_platform_driver!`. Constants define adapter index `0`, client address `0x30`, and board name `rust_driver_i2c`.

## Control Flow

When the parent platform device probes, the driver gets adapter 0 and creates an I2C client registration using the board info and parent device. The registration is stored in devres-backed state. `unbind()` logs lifecycle shutdown.

## State and Persistence Behavior

State is the parent device reference plus devres-managed I2C client registration. The registered child client persists until the platform driver instance is unbound.

## Dependencies and Integration Points

It depends on platform bus, OF/ACPI matching, built-in I2C, and an existing adapter 0. It pairs naturally with `rust_driver_i2c.rs`, whose id table can bind to the created client.

## Risks and Edge Cases

Hard-coding adapter 0 is fragile on real systems. If no adapter exists or address `0x30` conflicts, probe fails. The comments reference `rust_driver_platform` in a verification snippet, which appears copied and should not be treated as the module name.

## Test Signals

Load with a matching platform device and I2C adapter 0; verify the I2C client appears and can bind to the Rust I2C driver sample.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/rust/rust_i2c_client.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/rust/rust_minimal.rs -->
# sources/distributed-fs/ceph-client/samples/rust/rust_minimal.rs

## Purpose

This is the minimal Rust kernel module sample. It demonstrates module metadata, a typed module parameter, allocation into a kernel vector, init logging, and drop-time cleanup logging.

## Important APIs, Types, and Functions

It uses `module!`, `kernel::Module`, `ThisModule`, `KVec`, `GFP_KERNEL`, `module_parameters::test_parameter.value()`, `pr_info!`, and `Drop`.

## Control Flow

Module init logs startup, whether it is built-in, the `test_parameter` value, allocates a `KVec<i32>`, pushes three numbers, and returns `RustMinimal`. Drop logs the vector and exit message.

## State and Persistence Behavior

State is the `numbers` vector held by the module instance. The module parameter persists through module/kernel configuration while loaded.

## Dependencies and Integration Points

It depends on core Rust kernel allocation and module parameter support.

## Risks and Edge Cases

Allocation failure during vector pushes aborts module init. The sample has no synchronization needs because state is not shared after init.

## Test Signals

Load with default and custom `test_parameter`, verify init logs and unload logs, and build as both built-in and module where supported.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/rust/rust_minimal.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/rust/rust_misc_device.rs -->
# sources/distributed-fs/ceph-client/samples/rust/rust_misc_device.rs

## Purpose

This Rust module demonstrates a misc character device with per-open state, read/write iterators, and ioctl handling.

## Important APIs, Types, and Functions

It uses `MiscDeviceRegistration`, the `MiscDevice` trait, `File`, `Kiocb`, `IovIterDest`, `IovIterSource`, `UserSliceReader`, `UserSliceWriter`, ioctl helpers `_IO`, `_IOR`, `_IOW`, `Mutex<Inner>`, `KVVec<u8>`, and `PinnedDrop`. IOCTLs are `HELLO`, `GET_VALUE`, and `SET_VALUE`.

## Control Flow

Module init registers `/dev/rust-misc-device`. Each open allocates a pinned `RustMiscDevice` with value `0` and empty buffer. `write_iter()` replaces the buffer with user data and resets file position; `read_iter()` copies buffer contents respecting file position. `ioctl()` dispatches by command to set/get the integer value or log hello; unknown commands return `ENOTTY`.

## State and Persistence Behavior

State is per-open, not global: each file instance has its own mutex-protected `value` and `buffer`, plus a device reference. Data persists only for that open file handle. Drop logs when the per-open object exits.

## Dependencies and Integration Points

It integrates with miscdevice registration, VFS read/write/ioctl paths, user access APIs, and kernel Rust synchronization/allocation.

## Risks and Edge Cases

Large writes allocate into a `KVVec` and can fail. IOCTL argument size comes from command encoding; malformed user pointers return access errors. Per-open state may surprise users expecting global device state.

## Test Signals

Use the C example in comments: open the device, call hello, get/set/get value, perform read/write, and verify unknown ioctl fails.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/rust/rust_misc_device.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/rust/rust_print_events.c -->
# sources/distributed-fs/ceph-client/samples/rust/rust_print_events.c

## Purpose

This C companion file instantiates tracepoints used by the Rust printing sample.

## Important APIs, Types, and Functions

It defines `CREATE_TRACE_POINTS` and `CREATE_RUST_TRACE_POINTS`, then includes `<trace/events/rust_sample.h>`.

## Control Flow

There is no runtime function body. The preprocessor definitions cause tracepoint storage and registration code to be generated into this object during build.

## State and Persistence Behavior

Generated tracepoint descriptors become module/kernel static state for the linked `rust_print` object.

## Dependencies and Integration Points

It integrates C tracepoint generation with `rust_print_main.rs`, which declares and calls the Rust-visible tracepoint. The parent Makefile supplies include paths.

## Risks and Edge Cases

Exactly one object should create tracepoints for a given trace header. Missing include paths or mismatched header definitions break build/link.

## Test Signals

Build `rust_print`, load it, and confirm tracepoint availability plus invocation from Rust init.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/rust/rust_print_events.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/rust/rust_print_main.rs -->
# sources/distributed-fs/ceph-client/samples/rust/rust_print_main.rs

## Purpose

This Rust module demonstrates kernel Rust printing macros, formatting with Rust-owned values, dynamic dispatch through `Arc<dyn Display>`, `dbg!`, continued log lines, and calling a generated tracepoint.

## Important APIs, Types, and Functions

It uses `pr_emerg!` through `pr_info!`, `pr_cont!`, `Arc`, `UniqueArc`, `Display`, `dbg!`, `declare_trace!`, and a wrapper `trace_rust_sample_loaded()`. `arc_print()` exercises formatting modes for smart pointers and trait objects.

## Control Flow

Module init logs one message at each kernel log level, logs continued lines with and without format args, calls `arc_print()` to allocate and print `Arc`/`UniqueArc` values, then calls `trace::trace_rust_sample_loaded(42)`. Drop logs module exit.

## State and Persistence Behavior

The module is zero-sized after init; allocated Arcs are local and dropped before init completes. Tracepoint state is generated by the companion C object.

## Dependencies and Integration Points

It integrates with kernel logging, Rust allocation/sync primitives, and the C-generated `rust_sample_loaded` tracepoint from `rust_print_events.c`.

## Risks and Edge Cases

`dbg!` is intentionally allowed despite lint expectations and should not be copied into production code casually. Allocation failures in `arc_print()` fail module init.

## Test Signals

Load the module and inspect dmesg for all log levels and formatted Arc output; enable the Rust sample tracepoint and verify the `magic=42` event.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/rust/rust_print_main.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/rust/rust_soc.rs -->
# sources/distributed-fs/ceph-client/samples/rust/rust_soc.rs

## Purpose

This Rust platform driver sample demonstrates registering SoC bus attributes from a platform driver's probe.

## Important APIs, Types, and Functions

It uses OF/ACPI platform match tables, `soc::Attributes`, `soc::Registration`, `CString`, `pin_init_scope`, `ARef<platform::Device>`, and `module_platform_driver!`.

## Control Flow

Probe converts the platform device into an `ARef`, creates owned strings for machine, family, revision, serial number, and SoC id, packages them into `soc::Attributes`, and registers them through `soc::Registration::new()`. The registration is pinned in the driver instance.

## State and Persistence Behavior

Persistent state is the platform device reference and SoC registration. The registered attributes remain visible through SoC bus/sysfs while the driver is bound.

## Dependencies and Integration Points

It depends on platform bus matching and `SOC_BUS` support. It demonstrates how Rust drivers publish SoC identity metadata.

## Risks and Edge Cases

String allocation failures abort probe. Attribute values are fixed sample data, so they should not be used as real platform identifiers.

## Test Signals

Bind a matching OF or ACPI platform device, load the module, and inspect SoC bus/sysfs entries for the sample attributes.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/rust/rust_soc.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/seccomp/Makefile -->
# sources/distributed-fs/ceph-client/samples/seccomp/Makefile

## Purpose

This Makefile builds the seccomp user-space sample programs as kernel-tree user programs.

## Important APIs, Types, and Functions

It sets `userprogs-always-y += bpf-fancy dropper bpf-direct user-trap`, defines the composite `bpf-fancy-objs := bpf-fancy.o bpf-helper.o`, and adds `userccflags += -I usr/include`.

## Control Flow

Kbuild compiles all listed user programs unconditionally when this samples directory is built. `bpf-fancy` links with the helper object.

## State and Persistence Behavior

No runtime state is created by the Makefile; it affects build outputs only.

## Dependencies and Integration Points

It integrates with Kbuild user program rules and UAPI headers under `usr/include`.

## Risks and Edge Cases

The samples are architecture- and kernel-feature-sensitive. Missing UAPI seccomp headers or unsupported host architectures can limit build/runtime behavior.

## Test Signals

Build `samples/seccomp/` and verify the four user binaries are emitted.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/seccomp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/seccomp/bpf-direct.c -->
# sources/distributed-fs/ceph-client/samples/seccomp/bpf-direct.c

## Purpose

This x86-only user-space sample installs a seccomp BPF filter directly with raw `sock_filter` instructions and demonstrates `SECCOMP_RET_TRAP` by emulating writes to stderr in a SIGSYS handler.

## Important APIs, Types, and Functions

Key functions are `install_emulator()`, `emulator()`, `install_filter()`, and `main()`. It uses `sigaction(SIGSYS)`, `ucontext_t` register access, `prctl(PR_SET_NO_NEW_PRIVS)`, `prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER)`, BPF macros, `struct seccomp_data` offsets, and raw `syscall()`.

## Control Flow

The program installs a SIGSYS handler, then installs a filter allowing exit, sigreturn, stdin reads, stdout writes, trapping stderr writes, and killing other syscalls. It writes a prompt, reads a name, writes a greeting, and attempts a stderr write. The trap handler checks that the syscall is `write` to stderr, writes `[ERR] ` and the original buffer to stdout, and sets the syscall result register.

## State and Persistence Behavior

Seccomp mode is process-persistent after installation. The signal handler remains installed. No filesystem state is persisted.

## Dependencies and Integration Points

It is compiled only with full behavior on i386/x86_64 and uses architecture-specific syscall argument registers. It depends on seccomp filter support.

## Risks and Edge Cases

Register names and syscall numbers are architecture-sensitive. The handler performs writes from signal context for demonstration and does not fully handle EINTR or partial writes. Unsupported architectures return failure through a stub main.

## Test Signals

Run on x86, enter input, and confirm stderr output is redirected with `[ERR]`. Attempts to add disallowed syscalls should kill the process.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/seccomp/bpf-direct.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/seccomp/bpf-fancy.c -->
# sources/distributed-fs/ceph-client/samples/seccomp/bpf-fancy.c

## Purpose

This user-space sample builds a seccomp filter with label and comparison macros from `bpf-helper.h`, demonstrating readable construction of nontrivial BPF policy.

## Important APIs, Types, and Functions

It uses `struct bpf_labels`, macros `LOAD_SYSCALL_NR`, `SYSCALL`, `LABEL`, `JUMP`, `ARG`, `JEQ/JNE/JGE/JLT`, `ALLOW`, `DENY`, and helper `bpf_resolve_jumps()`. Runtime seccomp installation uses `prctl(PR_SET_NO_NEW_PRIVS)` and `prctl(PR_SET_SECCOMP)`.

## Control Flow

The filter allows exit syscalls, routes write and read checks through labels, permits reads only from stdin into the program's `buf` with length below the buffer, and permits writes only to stdout/stderr from known buffer addresses and bounded lengths. After installing the filter, the program prompts, reads, echoes through stderr, then intentionally writes too much from `msg2` to trigger the deny rule.

## State and Persistence Behavior

The label table is temporary setup state. The seccomp filter persists on the process after installation.

## Dependencies and Integration Points

It depends on `bpf-helper.c/h`, seccomp filter support, and stable local buffer addresses after filter installation.

## Risks and Edge Cases

The policy compares user pointer values to specific process addresses, so code changes that alter buffers must update the policy. The final over-length write is expected to kill the process.

## Test Signals

Run the program, provide input, observe allowed prompt/echo output, and verify the final write terminates the process under seccomp.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/seccomp/bpf-fancy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/seccomp/bpf-helper.c -->
# sources/distributed-fs/ceph-client/samples/seccomp/bpf-helper.c

## Purpose

This file implements helper functions for label-based seccomp BPF filter construction used by `bpf-fancy.c`.

## Important APIs, Types, and Functions

`bpf_resolve_jumps()` scans a filter and resolves pseudo-instructions emitted by `LABEL` and `JUMP`. `seccomp_bpf_label()` interns label names into `struct bpf_labels`. `seccomp_bpf_print()` dumps filter instructions for diagnostics.

## Control Flow

Label lookup either returns an existing label id or appends a new unresolved label with location `0xffffffff`. Jump resolution walks the filter backward by offset order, identifies `BPF_JA` instructions carrying sentinel `jt/jf` values, records label locations, or rewrites jump offsets to target labels. Duplicate or unresolved labels produce diagnostics and errors.

## State and Persistence Behavior

All mutable state is caller-owned `struct bpf_labels`. Resolved filters are modified in place before seccomp installation.

## Dependencies and Integration Points

It depends on Linux BPF instruction structures and the sentinel constants/macros from `bpf-helper.h`.

## Risks and Edge Cases

The helper only supports forward jumps because classic BPF disallows backward jumps. Label table overflow calls `exit(1)` in lookup. Invalid count values are rejected against `BPF_MAXINSNS`.

## Test Signals

Build and run `bpf-fancy`; unresolved or duplicate labels should produce explicit stderr messages. `seccomp_bpf_print()` can be used to inspect generated filters.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/seccomp/bpf-helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/seccomp/bpf-helper.h -->
# sources/distributed-fs/ceph-client/samples/seccomp/bpf-helper.h

## Purpose

This header provides macro helpers for constructing classic BPF seccomp filters with labels, syscall dispatch, argument loading, and width-aware comparisons.

## Important APIs, Types, and Functions

It defines `struct bpf_labels`, label sentinel values, `ALLOW`, `DENY`, `JUMP`, `LABEL`, `SYSCALL`, `FIND_LABEL`, `LOAD_SYSCALL_NR`, and `ARG`. It maps comparison macros `JEQ/JNE/JGT/JLT/JGE/JLE/JA` to 32-bit or 64-bit implementations based on `__BITS_PER_LONG`, and handles endian-specific argument offsets.

## Control Flow

The macros expand to arrays of `struct sock_filter` instructions. On 64-bit targets, `ARG_64` loads low and high halves into BPF memory slots and comparison macros preserve the high half in `A` after nested jumps. Label macros emit unresolved jump pseudo-instructions later fixed by `bpf_resolve_jumps()`.

## State and Persistence Behavior

The header itself holds no state. State is in the caller's label table and generated filter array.

## Dependencies and Integration Points

It integrates with Linux UAPI BPF/seccomp headers, endian definitions, and `asm/bitsperlong.h`.

## Risks and Edge Cases

Macro expansion is subtle and sensitive to BPF accumulator/memory invariants. Pointer comparisons in filters can be unsafe if buffers move. Unsupported word sizes trigger preprocessor errors.

## Test Signals

Compile on 32-bit and 64-bit architectures where possible, run `bpf-fancy`, and inspect generated filter dumps for correct jump offsets and argument comparisons.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/seccomp/bpf-helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/seccomp/dropper.c -->
# sources/distributed-fs/ceph-client/samples/seccomp/dropper.c

## Purpose

This user-space utility installs a simple seccomp filter that returns a chosen errno, or kills, for one syscall number on one audit architecture before executing another program.

## Important APIs, Types, and Functions

The main functions are `install_filter()` and `main()`. It uses `AUDIT_ARCH_*`, BPF statements over `struct seccomp_data.arch` and `.nr`, `SECCOMP_RET_ERRNO`, `SECCOMP_RET_KILL`, `prctl(PR_SET_NO_NEW_PRIVS)`, `prctl(PR_SET_SECCOMP)`, and `execv()`.

## Control Flow

`main()` parses `arch`, `syscall_nr`, `errno`, program path, and arguments. `install_filter()` builds a short filter: if arch matches and syscall number matches, return the configured errno or kill action; otherwise allow. After installing it, `main()` execs the target program.

## State and Persistence Behavior

The seccomp filter persists across `execv()`, so it constrains the launched program. No other state is persisted.

## Dependencies and Integration Points

It depends on seccomp filter support and audit architecture constants. It is useful for fault-injection against arbitrary programs.

## Risks and Edge Cases

An incorrect architecture value silently allows all syscalls on the real arch. `errno` is masked through `SECCOMP_RET_DATA`. Filtering essential syscalls can make the target fail before meaningful testing.

## Test Signals

Run with `AUDIT_ARCH_X86_64`, a target syscall such as `openat`, and a small command; verify the syscall returns the selected errno or the process is killed with `-1`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/seccomp/dropper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/seccomp/user-trap.c -->
# sources/distributed-fs/ceph-client/samples/seccomp/user-trap.c

## Purpose

This user-space sample demonstrates seccomp user notification. A worker installs a filter that traps `mount(2)` to a listener fd, drops privileges, and a tracer process decides whether to perform bind mounts on its behalf.

## Important APIs, Types, and Functions

Important functions are `seccomp()`, `send_fd()`, `recv_fd()`, `user_trap_syscall()`, `handle_req()`, and `main()`. It uses `SECCOMP_FILTER_FLAG_NEW_LISTENER`, `SECCOMP_RET_USER_NOTIF`, `SECCOMP_IOCTL_NOTIF_RECV`, `SECCOMP_IOCTL_NOTIF_SEND`, `SECCOMP_IOCTL_NOTIF_ID_VALID`, fd passing with `SCM_RIGHTS`, `/proc/<pid>/mem`, and `mount()/umount2()`.

## Control Flow

The parent creates a socketpair and forks a worker. The worker installs a listener-trapping mount filter, drops to uid 1000, sends the listener fd to the parent, attempts a disallowed mount, then attempts an allowed `/tmp/foo` bind mount. The parent forks a tracer, which loops receiving seccomp notifications, validates the trapped syscall, reads source/target strings from the worker's memory after validating notification id, permits only bind mounts where both paths begin `/tmp/`, performs the mount itself, and replies.

## State and Persistence Behavior

State spans three processes: socketpair fd passing, listener fd, notification request/response buffers, `/tmp/foo`, and any successful bind mount. Cleanup kills helper processes, detaches the mount, and removes the directory.

## Dependencies and Integration Points

It depends on modern seccomp user notification APIs, mount permissions in the tracer, `/proc/<pid>/mem`, and local Unix sockets.

## Risks and Edge Cases

The sample explicitly discusses TOCTOU risks and uses `SECCOMP_IOCTL_NOTIF_ID_VALID` after opening task memory. It still has sample-grade string reading and policy. Running it mutates `/tmp/foo` and mount namespace state.

## Test Signals

Run as a user allowed to perform the tracer-side bind mount. The bad mount should fail with `EPERM`, the `/tmp/foo` bind mount should succeed, and cleanup should remove the directory.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/seccomp/user-trap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/timers/Makefile -->
# sources/distributed-fs/ceph-client/samples/timers/Makefile

## Purpose

This Makefile builds the HPET user-space sample program.

## Important APIs, Types, and Functions

It sets `userprogs-always-y += hpet_example` and adds `userccflags += -I usr/include`.

## Control Flow

Kbuild compiles `hpet_example.c` as a user program when the timers samples are built.

## State and Persistence Behavior

Only build artifacts are affected.

## Dependencies and Integration Points

It integrates with UAPI headers for HPET ioctl constants.

## Risks and Edge Cases

The resulting binary needs an HPET device node and kernel HPET support at runtime.

## Test Signals

Build samples and verify `hpet_example` is produced.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/timers/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/timers/hpet_example.c -->
# sources/distributed-fs/ceph-client/samples/timers/hpet_example.c

## Purpose

This user-space sample exercises HPET character device operations: open/close, query info, polling periodic interrupts, and asynchronous SIGIO notification.

## Important APIs, Types, and Functions

The command table dispatches to `hpet_open_close()`, `hpet_info()`, `hpet_poll()`, and `hpet_fasync()`. It uses `open`, `close`, HPET ioctls `HPET_INFO`, `HPET_IRQFREQ`, `HPET_EPI`, `HPET_IE_ON`, `poll`, `read`, `fcntl(F_SETOWN/F_GETFL/F_SETFL|O_ASYNC)`, `signal(SIGIO)`, `pause`, and `gettimeofday`.

## Control Flow

`main()` removes the program name, looks up the first argument in the command table, and calls the matching handler. `open-close` only validates open. `info` prints `struct hpet_info`. `poll` configures interrupt frequency, enables periodic mode when supported, enables interrupts, then polls and reads expiration counts for the requested iterations. `fasync` installs a SIGIO handler, configures async ownership and frequency, enables interrupts, and waits for signals.

## State and Persistence Behavior

Runtime state is the HPET fd configuration, process signal handler, and global `hpet_sigio_count`. Device interrupt settings are active while fd is open.

## Dependencies and Integration Points

It depends on `/dev/hpet` or another HPET device path, HPET UAPI headers, and kernel HPET support.

## Risks and Edge Cases

The code checks some `fcntl` calls against `== 1`, which is unusual because errors are `-1`; this may miss failures. Frequency and iteration parsing uses `atoi` without validation. Poll and signal loops can block indefinitely.

## Test Signals

Run `hpet_example info /dev/hpet`, then `poll /dev/hpet <freq> <iterations>` and `fasync /dev/hpet <freq> <iterations>` on HPET-capable hardware.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/timers/hpet_example.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/trace_events/Makefile -->
# sources/distributed-fs/ceph-client/samples/trace_events/Makefile

## Purpose

This Kbuild file builds trace event sample modules and configures include paths so trace headers outside `include/trace/events` can be found.

## Important APIs, Types, and Functions

It sets `CFLAGS_trace-events-sample.o := -I$(src)` and `CFLAGS_trace_custom_sched.o := -I$(src)`, then maps `CONFIG_SAMPLE_TRACE_EVENTS` and `CONFIG_SAMPLE_TRACE_CUSTOM_EVENTS` to their objects.

## Control Flow

Kbuild applies object-specific CFLAGS before compiling the files that define tracepoints or custom events.

## State and Persistence Behavior

No runtime state; it controls build configuration.

## Dependencies and Integration Points

It integrates with the tracepoint code-generation mechanism that includes headers via `define_trace.h` and `define_custom_trace.h`.

## Risks and Edge Cases

Removing `-I$(src)` can make generated trace includes fail. Each trace header must have exactly one C file that creates the tracepoints.

## Test Signals

Enable both configs and verify both modules build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/trace_events/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/trace_events/trace-events-sample.c -->
# sources/distributed-fs/ceph-client/samples/trace_events/trace-events-sample.c

## Purpose

This kernel module exercises custom trace events defined in `trace-events-sample.h` by emitting them from kernel threads.

## Important APIs, Types, and Functions

It defines `CREATE_TRACE_POINTS`, includes the sample trace header, uses `kthread_run`, `kthread_stop`, `schedule_timeout`, `trace_foo_bar`, event-template trace functions, `trace_foo_rel_loc`, and registration callbacks `foo_bar_reg()`/`foo_bar_unreg()`.

## Control Flow

Module init starts `event-sample`, which loops once per second building arrays and emitting a variety of tracepoints. Trace events with `_FN` registration callbacks start a second thread `event-sample-fn` only when those tracepoints are enabled; callbacks maintain `simple_thread_cnt` under `thread_mutex`. Module exit stops the base thread and any active function-triggered thread.

## State and Persistence Behavior

Global state includes thread task pointers, `thread_mutex`, and the registration count. Trace ring buffer state is managed by ftrace/perf infrastructure.

## Dependencies and Integration Points

It depends on the kernel tracing subsystem, kthreads, scheduler timeouts, and the generated tracepoint definitions from its header.

## Risks and Edge Cases

Registration callbacks must coordinate with module unload to avoid running threads after removal. Tracepoint format changes affect user-space parsers. The sample intentionally emits frequent events once enabled.

## Test Signals

Load the module, enable events under `/sys/kernel/tracing/events/sample-trace/`, observe emitted records, then disable `_fn` events and verify the auxiliary thread stops.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/trace_events/trace-events-sample.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/trace_events/trace-events-sample.h -->
# sources/distributed-fs/ceph-client/samples/trace_events/trace-events-sample.h

## Purpose

This trace header is an extensive sample of Linux trace event declarations, including dynamic arrays, strings, bitmasks, cpumasks, event conditions, registration callbacks, event classes, custom print formats, and relative-location fields.

## Important APIs, Types, and Functions

It defines `TRACE_SYSTEM sample-trace`, `TRACE_SYSTEM_VAR sample_trace`, helper `__length_of()`, enum constants with `TRACE_DEFINE_ENUM`, `TRACE_EVENT(foo_bar)`, `TRACE_EVENT_CONDITION`, `TRACE_EVENT_FN`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `DEFINE_EVENT_CONDITION`, `DEFINE_EVENT_FN`, `DEFINE_EVENT_PRINT`, and `TRACE_EVENT(foo_rel_loc)`.

## Control Flow

The header is included multiple times by trace generation machinery. Event macros generate tracepoint call sites, record formats, assignment code, print formatting, and enable/disable hooks. The final include of `<trace/define_trace.h>` outside the guard creates definitions when `CREATE_TRACE_POINTS` is set.

## State and Persistence Behavior

Generated tracepoints and event metadata are static module state. Runtime records are stored in tracing ring buffers when events are enabled.

## Dependencies and Integration Points

It depends on `linux/tracepoint.h`, define-trace include rules, and registration functions implemented in the C file.

## Risks and Edge Cases

Trace headers must be multi-read safe and keep include path macros correct. Dynamic data length calculations must match assignment and print logic. User-space tooling can depend on enum and format metadata.

## Test Signals

Build the module, inspect event `format` files, enable each event type, and confirm printed fields match emitted data.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/trace_events/trace-events-sample.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/trace_events/trace_custom_sched.c -->
# sources/distributed-fs/ceph-client/samples/trace_events/trace_custom_sched.c

## Purpose

This module demonstrates attaching custom trace events to existing scheduler tracepoints.

## Important APIs, Types, and Functions

It includes `<trace/events/sched.h>`, defines `CREATE_CUSTOM_TRACE_EVENTS`, includes `trace_custom_sched.h`, uses `for_each_kernel_tracepoint()`, and calls generated helpers `trace_custom_event_sched_switch_update()` and `trace_custom_event_sched_waking_update()`.

## Control Flow

Module init iterates all kernel tracepoints and passes each to `fct()`, which asks the generated custom-event helpers to attach to matching scheduler tracepoints. Exit has no explicit teardown because trace custom event infrastructure owns lifecycle.

## State and Persistence Behavior

Generated custom event metadata is module state. Event records appear in tracing buffers when enabled.

## Dependencies and Integration Points

It depends on scheduler trace event declarations and the custom trace event mechanism.

## Risks and Edge Cases

The custom event prototypes in the header must match existing scheduler tracepoint prototypes exactly. Tracepoint symbol availability and non-exported events are handled by iteration rather than direct references.

## Test Signals

Load the module, inspect custom scheduler event entries in tracing, enable them, and trigger task switches/wakes.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/trace_events/trace_custom_sched.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/trace_events/trace_custom_sched.h -->
# sources/distributed-fs/ceph-client/samples/trace_events/trace_custom_sched.h

## Purpose

This header declares custom trace events derived from existing scheduler tracepoints with reduced/custom payloads.

## Important APIs, Types, and Functions

It uses `TRACE_CUSTOM_EVENT(sched_switch, ...)` and `TRACE_CUSTOM_EVENT(sched_waking, ...)`, defining custom `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk` sections. It ends with `TRACE_INCLUDE_PATH .`, `TRACE_INCLUDE_FILE trace_custom_sched`, and `<trace/define_custom_trace.h>`.

## Control Flow

The header is parsed multiple times by the trace macro system. The custom sched_switch event records previous priority, next pid, and next priority. The sched_waking event records pid and priority.

## State and Persistence Behavior

Generated custom event descriptors and format metadata persist while the module is loaded. Data is recorded only when the custom events are enabled.

## Dependencies and Integration Points

It depends on `linux/trace_events.h`, scheduler tracepoint prototypes included by the C file, and the custom trace generator.

## Risks and Edge Cases

Prototype mismatch with upstream scheduler events causes build breakage or incorrect records. Include-file macros must remain outside the guard.

## Test Signals

Build and load the module, inspect custom event `format` files, enable them, and verify priority/pid output during scheduling activity.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/trace_events/trace_custom_sched.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/trace_printk/Makefile -->
# sources/distributed-fs/ceph-client/samples/trace_printk/Makefile

## Purpose

This Kbuild file builds the `trace-printk` sample module when `CONFIG_SAMPLE_TRACE_PRINTK` is enabled.

## Important APIs, Types, and Functions

It maps `obj-$(CONFIG_SAMPLE_TRACE_PRINTK) += trace-printk.o`.

## Control Flow

Kbuild includes the object as built-in or module depending on the config.

## State and Persistence Behavior

No runtime state is created by the Makefile.

## Dependencies and Integration Points

The C file depends on tracing and IRQ work APIs.

## Risks and Edge Cases

Only build selection is represented here; Kconfig must ensure tracing prerequisites.

## Test Signals

Enable the config and verify `trace-printk.o` or module output.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/trace_printk/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/trace_printk/trace-printk.c -->
# sources/distributed-fs/ceph-client/samples/trace_printk/trace-printk.c

## Purpose

This module exercises `trace_printk()` paths for static strings, dynamic strings, formatted strings, and IRQ context.

## Important APIs, Types, and Functions

It defines global non-static strings to force dynamic-string behavior, an `irq_work` item, `trace_printk_irq_work()`, `trace_printk_init()`, and `trace_printk_exit()`. It uses `trace_printk`, `init_irq_work`, `irq_work_queue`, and `irq_work_sync`.

## Control Flow

Module init initializes irq work, emits static and dynamic trace_printk calls in process context, queues and synchronously waits for IRQ work that emits similar calls in IRQ context, then emits formatted static and dynamic strings. Exit does nothing.

## State and Persistence Behavior

Global strings and `irqwork` are module state. Trace output persists in tracing buffers according to tracing configuration.

## Dependencies and Integration Points

It depends on trace_printk support and IRQ work. It is meant to test tracing internals, not as production logging guidance.

## Risks and Edge Cases

`trace_printk()` is expensive and inappropriate for production fast paths. Dynamic format strings exercise less optimized paths. IRQ context output tests context safety.

## Test Signals

Load the module and inspect `/sys/kernel/tracing/trace` or trace_pipe for expected process and IRQ messages.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/trace_printk/trace-printk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/tsm-mr/Makefile -->
# sources/distributed-fs/ceph-client/samples/tsm-mr/Makefile

## Purpose

This Kbuild fragment builds the TSM measurement-register sample module.

## Important APIs, Types, and Functions

It maps `obj-$(CONFIG_SAMPLE_TSM_MR) += tsm_mr_sample.o`.

## Control Flow

Kbuild includes the object when the config is enabled.

## State and Persistence Behavior

Only build output is affected.

## Dependencies and Integration Points

The C file depends on the TSM measurement-register framework, miscdevice, and crypto hashing.

## Risks and Edge Cases

Kconfig must provide required dependencies.

## Test Signals

Enable `CONFIG_SAMPLE_TSM_MR` and verify the module builds.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/tsm-mr/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/tsm-mr/tsm_mr_sample.c -->
# sources/distributed-fs/ceph-client/samples/tsm-mr/tsm_mr_sample.c

## Purpose

This module demonstrates exposing emulated Trusted Security Module measurement registers through the `tsm-mr` framework and a misc device.

## Important APIs, Types, and Functions

It defines `sample_report` with several digest buffers, `sample_report_refresh()`, `sample_report_extend_mr()`, `sample_mrs[]`, `sample_tm`, `sample_misc_dev`, init and exit functions. It uses SHA-256/384/512 helpers, `TSM_MR_` macros, flags such as `TSM_MR_F_NOHASH`, `TSM_MR_F_LIVE`, `TSM_MR_F_RTMR`, and `tsm_mr_create_attribute_group()`.

## Control Flow

Init creates a TSM MR attribute group from `sample_tm` and registers a misc device with that group. Reads of live registers can call `refresh`, which recomputes `report_digest` over the report structure before the digest field. Writes/extensions call `sample_report_extend_mr()`, which hashes old MR value plus provided data according to the MR's algorithm. Exit deregisters the misc device and frees the group.

## State and Persistence Behavior

All MR values live in the static `sample_report` structure and persist while the module is loaded. Extending RTMR-capable registers mutates those digest buffers.

## Dependencies and Integration Points

It depends on the TSM MR framework, miscdevice sysfs group support, and kernel crypto SHA helpers.

## Risks and Edge Cases

This is emulated data, not hardware-rooted trust. Unsupported algorithms return `-EOPNOTSUPP`. The copyright year range appears malformed (`2024-2005`) but is not runtime behavior.

## Test Signals

Load the module, inspect misc-device sysfs attributes, read static/live MRs, extend writable RTMRs, and confirm digest changes.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/tsm-mr/tsm_mr_sample.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/uhid/Makefile -->
# sources/distributed-fs/ceph-client/samples/uhid/Makefile

## Purpose

This Makefile builds the UHID user-space example program.

## Important APIs, Types, and Functions

It sets `userprogs-always-y += uhid-example` and includes UAPI headers with `userccflags += -I usr/include`.

## Control Flow

Kbuild compiles `uhid-example.c` as a user program.

## State and Persistence Behavior

Only build artifacts are produced.

## Dependencies and Integration Points

The sample uses `/dev/uhid` and Linux UHID UAPI headers.

## Risks and Edge Cases

Runtime requires UHID support and usually root or device permissions.

## Test Signals

Build samples and verify `uhid-example` is produced.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/uhid/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/uhid/uhid-example.c -->
# sources/distributed-fs/ceph-client/samples/uhid/uhid-example.c

## Purpose

This user-space example creates a virtual HID device through `/dev/uhid`: a three-button mouse with wheel and LED output report handling.

## Important APIs, Types, and Functions

It defines a HID report descriptor `rdesc`, helper `uhid_write()`, lifecycle functions `create()` and `destroy()`, event reader `event()`, output parser `handle_output()`, input sender `send_event()`, keyboard handler `keyboard()`, and `main()`. It uses `struct uhid_event`, `UHID_CREATE`, `UHID_DESTROY`, `UHID_INPUT`, `UHID_OUTPUT`, `poll`, `termios`, and global button/movement state.

## Control Flow

`main()` puts stdin in noncanonical mode, opens `/dev/uhid` or a supplied path, creates the virtual device, and polls stdin plus the UHID fd. Keyboard commands toggle buttons or set relative movement/wheel deltas and call `send_event()`. UHID events from the kernel are logged; output reports for report id 2 are decoded as LED flags. On exit or error, the program sends `UHID_DESTROY`.

## State and Persistence Behavior

Global booleans track button state, and signed chars hold one-shot movement/wheel deltas reset after each event. The virtual HID device persists until destroyed or the fd closes.

## Dependencies and Integration Points

It depends on UHID, input/HID subsystems, terminal stdin, and access to `/dev/uhid`. Resulting devices integrate with evdev and HID debugfs.

## Risks and Edge Cases

The code modifies terminal mode without restoring the original state. `uhid_write()` compares short write size against `sizeof(ev)`, which is size of pointer in the diagnostic expression, though the earlier `ret != sizeof(*ev)` check is correct. Running creates a real input device.

## Test Signals

Run as permitted user, observe a new HID/evdev mouse, press movement/button keys, verify pointer/input events, and write LED events through evdev to see output reports logged.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/uhid/uhid-example.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/user_events/Makefile -->
# sources/distributed-fs/ceph-client/samples/user_events/Makefile

## Purpose

This Makefile builds the user_events sample program with direct compile rules.

## Important APIs, Types, and Functions

It sets `CFLAGS += -Wl,-no-as-needed -Wall -I../../usr/include`, declares `example: example.o`, and `example.o: example.c`.

## Control Flow

Unlike Kbuild `userprogs` fragments, this is a simple make rule for compiling and linking `example`.

## State and Persistence Behavior

Only the built executable/object are affected.

## Dependencies and Integration Points

It depends on user_events UAPI headers and linker behavior retaining needed libraries/objects.

## Risks and Edge Cases

The include path is relative and assumes invocation from this directory. It does not define a clean target.

## Test Signals

Run `make` in the directory and verify `example` builds.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/user_events/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/user_events/example.c -->
# sources/distributed-fs/ceph-client/samples/user_events/example.c

## Purpose

This user-space program demonstrates the `user_events` tracing ABI by registering an event and writing records only when tracing is attached.

## Important APIs, Types, and Functions

It uses `/sys/kernel/tracing/user_events_data`, `struct user_reg`, ioctl `DIAG_IOCSREG`, `writev`, `struct iovec`, and a global `enabled` bit. `event_reg()` sets registration fields, including `enable_bit=31`, `enable_addr`, and event command string.

## Control Flow

`main()` opens the data file, registers event `"test u32 count"`, builds an iovec containing the write index and a count payload, then loops waiting for Enter. If the kernel has set the enabled bit, it writes the event record with `writev`, increments the count, and prints a message.

## State and Persistence Behavior

Process state includes `enabled`, write index, and `count`. The registered user event persists while the fd/process registration remains active in tracing infrastructure.

## Dependencies and Integration Points

It depends on tracingfs mounted at `/sys/kernel/tracing`, user_events support, and trace consumers enabling the event.

## Risks and Edge Cases

The program does not check `open()` failure before ioctl. It loops forever via `goto ask`. Event writes are skipped unless tracing is attached, which is intended but can look idle.

## Test Signals

Run the program, enable the corresponding user event in tracing, press Enter repeatedly, and confirm count records appear in trace output.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/user_events/example.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/v4l/Makefile -->
# sources/distributed-fs/ceph-client/samples/v4l/Makefile

## Purpose

This Kbuild fragment builds the V4L2 PCI skeleton sample driver.

## Important APIs, Types, and Functions

It maps `obj-$(CONFIG_VIDEO_PCI_SKELETON) := v4l2-pci-skeleton.o`.

## Control Flow

Kbuild compiles the sample when the video skeleton config is enabled.

## State and Persistence Behavior

No runtime state is created by the Makefile.

## Dependencies and Integration Points

The source depends on PCI, V4L2, controls, events, and videobuf2 DMA-contig APIs.

## Risks and Edge Cases

Kconfig must select the relevant media dependencies.

## Test Signals

Enable `CONFIG_VIDEO_PCI_SKELETON` and verify the module builds.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/v4l/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/v4l/v4l2-pci-skeleton.c -->
# sources/distributed-fs/ceph-client/samples/v4l/v4l2-pci-skeleton.c

## Purpose

This is a V4L2 PCI capture-driver skeleton. It shows the structure of a PCI video receiver with one S-Video input, one HDMI input, V4L2 controls, format/timing negotiation, and videobuf2 capture queue integration.

## Important APIs, Types, and Functions

Core types are `struct skeleton`, holding PCI, V4L2 device/video_device, control handler, queue, format, input, standard, timings, and buffer list state, plus `struct skel_buffer`. Important functions include `queue_setup()`, `buffer_prepare()`, `buffer_queue()`, `return_all_buffers()`, `start_streaming()`, `stop_streaming()`, format/std/timings/input ioctls, `skeleton_s_ctrl()`, `skeleton_probe()`, and `skeleton_remove()`. It uses `vb2_queue`, `vb2_dma_contig_memops`, and V4L2 ioctl/file helpers.

## Control Flow

Probe enables PCI, sets a 32-bit DMA mask, allocates state, requests IRQ, initializes default 720p60 timings and PAL-ish SD standard, registers the V4L2 device, creates controls, initializes the vb2 queue, initializes buffer lists/spinlock, fills `video_device`, and registers a video node. User ioctls query/set formats, standards, timings, and inputs; streaming ioctls are delegated to vb2 callbacks. Remove unregisters video/V4L2 resources and disables PCI.

## State and Persistence Behavior

Per-device state persists in `struct skeleton`. Buffer queue state is protected by `qlock`; ioctl and streaming serialization uses `lock`. Current input controls whether SDTV or HDMI timing APIs are valid. Sequence and field state update during streaming.

## Dependencies and Integration Points

It integrates with PCI driver registration, V4L2 core, vb2, DMA-contig memory, controls, events, and media user APIs.

## Risks and Edge Cases

Many hardware operations are TODO stubs, including IRQ frame completion, DMA start/stop, std/timing hardware programming, and controls. The PCI id table is empty, so it will not bind without editing. `skeleton_remove()` expects `pci_get_drvdata()` to return `v4l2_dev`, but probe does not set PCI drvdata explicitly in the shown code, which is a notable skeleton gap.

## Test Signals

Compile-test the module, add a PCI id for experimentation, run `v4l2-compliance`, exercise format/input/timing ioctls, and verify vb2 buffer setup paths reject busy/invalid state correctly.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/v4l/v4l2-pci-skeleton.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/vfio-mdev/Makefile -->
# sources/distributed-fs/ceph-client/samples/vfio-mdev/Makefile

## Purpose

This Kbuild file builds mediated-device VFIO sample modules for serial and display devices.

## Important APIs, Types, and Functions

It maps configs to objects: `mtty.o`, `mdpy.o`, `mdpy-fb.o`, and `mbochs.o`.

## Control Flow

Kbuild includes each sample object when its `CONFIG_SAMPLE_VFIO_MDEV_*` symbol is enabled.

## State and Persistence Behavior

Only build outputs are affected.

## Dependencies and Integration Points

The modules integrate with VFIO, mediated devices, PCI-like emulation, framebuffer, and DMA-BUF depending on the selected sample.

## Risks and Edge Cases

These samples depend on VFIO/mdev APIs that can change; Kconfig must provide the required dependencies.

## Test Signals

Enable the sample configs and verify all selected modules build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/vfio-mdev/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/vfio-mdev/mbochs.c -->
# sources/distributed-fs/ceph-client/samples/vfio-mdev/mbochs.c

## Purpose

`mbochs.c` implements a mediated VFIO virtual PCI display device that emulates enough of QEMU/Bochs stdvga for guests such as `bochs-drm` to use a framebuffer, MMIO VBE registers, EDID region, mmap, and DMA-BUF graphics plane export.

## Important APIs, Types, and Functions

Core state is `struct mdev_state`, containing `vfio_device`, virtual config space, BAR masks, VBE registers, video-memory pages, EDID registers/blob, dmabuf list, and locks. `struct mbochs_type` defines small/medium/large mdev types; `struct mbochs_mode` describes an active framebuffer; `struct mbochs_dmabuf` tracks exported framebuffers. Major functions include `mbochs_create_config_space()`, `mbochs_check_framebuffer()`, access handlers for PCI config/MMIO/EDID/memory BAR, `mbochs_init_dev()`, `mbochs_probe()`, read/write/mmap operations, page fault handlers, DMA-BUF map/unmap/release/export helpers, VFIO region/device/ioctl handlers, and module init/exit.

## Control Flow

Module init allocates a char-device range, registers the mdev driver, class, parent device, and three mdev types. Creating an mdev allocates VFIO state and registers an emulated IOMMU VFIO device. Device init reserves memory from the atomic MB pool, allocates config/page arrays, sets EDID limits, builds PCI config space, and resets VBE registers. VFIO reads/writes dispatch by file offset to config, MMIO, EDID, or memory BAR handlers. Guest VBE writes define the framebuffer; `VFIO_DEVICE_QUERY_GFX_PLANE` validates it and creates or finds a matching dmabuf; `VFIO_DEVICE_GET_GFX_DMABUF` exports it to an fd.

## State and Persistence Behavior

Global state includes class/device/cdev/parent registration and `mbochs_avail_mbytes`. Per-mdev state persists until removal: virtual config, VBE registers, lazily allocated pages, EDID content, active plane id, and dmabuf list. Pages are allocated on access or dmabuf creation and released on close. DMA-BUF objects can outlive list unlinking until their release callback drops page references.

## Dependencies and Integration Points

It depends on VFIO, mdev, emulated IOMMU iommufd helpers, PCI constants, DMA-BUF, DRM fourcc/plane definitions, page fault/mmap APIs, sysfs attributes, and guest drivers expecting Bochs VBE behavior.

## Risks and Edge Cases

Memory accounting is global MB-based and must be balanced on init/release errors. `mdev_access()` memory BAR offset subtracts `MBOCHS_MMIO_BAR_OFFSET` rather than `MBOCHS_MEMORY_BAR_OFFSET`, which is suspicious in a sample and deserves scrutiny. Framebuffer validation only supports 32 bpp XRGB8888 and rejects small/overflowing modes. DMA-BUF export requires page-aligned offsets. Locking around dmabuf list and page references is delicate.

## Test Signals

Load the module, create each mdev type under sysfs, bind it to VFIO, query VFIO regions, boot a guest with the mdev, verify Bochs DRM detects a display, change VBE modes, query/export graphics planes, mmap BAR0, and check available memory counts before/after removal.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/vfio-mdev/mbochs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/vfio-mdev/mdpy-defs.h -->
# sources/distributed-fs/ceph-client/samples/vfio-mdev/mdpy-defs.h

## Purpose

This header defines the simple virtual PCI display device ABI used by the `mdpy` mediated display and its framebuffer driver.

## Important APIs, Types, and Functions

It defines PCI vendor/device/subsystem ids and vendor capability offsets: `MDPY_VENDORCAP_OFFSET`, `MDPY_VENDORCAP_SIZE`, `MDPY_FORMAT_OFFSET`, `MDPY_WIDTH_OFFSET`, and `MDPY_HEIGHT_OFFSET`.

## Control Flow

There is no executable control flow. Producers write these config-space fields, and `mdpy-fb.c` reads them during PCI probe.

## State and Persistence Behavior

The constants describe config-space state exposed by the virtual PCI device.

## Dependencies and Integration Points

It depends on PCI id constants and DRM fourcc values used by the driver code.

## Risks and Edge Cases

Changing offsets or IDs breaks compatibility between the virtual device and framebuffer driver.

## Test Signals

Verify `mdpy-fb.c` matches devices using the IDs and reads format/width/height from the declared offsets.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/vfio-mdev/mdpy-defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/vfio-mdev/mdpy-fb.c -->
# sources/distributed-fs/ceph-client/samples/vfio-mdev/mdpy-fb.c

## Purpose

This PCI framebuffer driver binds to the simple `mdpy` virtual PCI display device and registers a Linux framebuffer over BAR0.

## Important APIs, Types, and Functions

It defines fixed and variable framebuffer templates, `struct mdpy_fb_par` with pseudo palette, `mdpy_fb_setcolreg()`, `mdpy_fb_destroy()`, `mdpy_fb_probe()`, `mdpy_fb_remove()`, the PCI id table, and module init. It uses PCI region management, config-space reads, `ioremap`, `framebuffer_alloc`, `register_framebuffer`, `FB_DEFAULT_IOMEM_OPS`, and DRM format `DRM_FORMAT_XRGB8888`.

## Control Flow

Probe enables the PCI device, requests regions, reads format/width/height from vendor capability config offsets, validates XRGB8888 and sane dimensions, allocates `fb_info`, maps BAR0, fills fix/var screeninfo, assigns fbops and pseudo palette, then registers the framebuffer. Remove unregisters the framebuffer, unmaps BAR0, releases regions, and disables the device.

## State and Persistence Behavior

Framebuffer state lives in `fb_info`, mapped BAR0 memory, and `mdpy_fb_par` palette. The framebuffer device persists until PCI removal/module unload. Color register changes update only the pseudo palette.

## Dependencies and Integration Points

It integrates with PCI, fbdev, DRM fourcc definitions, and the mdpy virtual PCI ABI from `mdpy-defs.h`.

## Risks and Edge Cases

Only XRGB8888 is supported. Width/height are trusted after coarse range checks. `mdpy_fb_destroy()` unmaps `screen_base`, and remove also unmaps directly; fbdev destroy ordering should be verified to avoid double-unmap paths.

## Test Signals

Expose an mdpy mdev/PCI device, load the driver, confirm `fb%d registered`, write to `/dev/fb*`, and verify remove cleanup with no leaks or mapping warnings.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/vfio-mdev/mdpy-fb.c -->
