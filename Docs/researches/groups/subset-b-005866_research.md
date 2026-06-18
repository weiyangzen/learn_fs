# subset-b-005866 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iova_bitmap.h -->
# sources/distributed-fs/ceph-client/include/linux/iova_bitmap.h

## Purpose
`iova_bitmap.h` declares the optional IOVA dirty/coverage bitmap helper used by IOMMUFD driver code. It gives callers an opaque bitmap object for a starting IOVA range, page size, and user buffer, then lets them mark subranges and iterate populated entries.

## Important APIs, types, and functions
The public contract is `struct iova_bitmap`, `iova_bitmap_fn_t`, `iova_bitmap_alloc`, `iova_bitmap_free`, `iova_bitmap_for_each`, and `iova_bitmap_set`. Disabled builds provide stubs returning `NULL`, `-EOPNOTSUPP`, or no-op behavior.

## Control flow
Callers allocate a bitmap, set IOVA intervals, iterate them through a callback, and free the object. The header gates all real work on `CONFIG_IOMMUFD_DRIVER`.

## State and persistence
State is entirely in the opaque bitmap and the user-provided bitmap storage. There is no persistent state.

## Dependencies and integration points
It depends on Linux integer types, `errno`, `__user` pointers, and the IOMMUFD driver implementation.

## Risks and test signals
Risks are page-size/range alignment mistakes, unsafe user-buffer access in the implementation, and callers not handling disabled stubs. Tests should cover disabled configs, empty bitmaps, partial ranges, large IOVA spans, and callback error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iova_bitmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ip.h -->
# sources/distributed-fs/ceph-client/include/linux/ip.h

## Purpose
`ip.h` supplies kernel IPv4 header accessors layered over `sk_buff` network and transport offsets, plus helpers for total length handling in normal packets and TCP GSO packets.

## Important APIs, types, and functions
Important helpers are `ip_hdr`, `inner_ip_hdr`, `ipip_hdr`, `ip_transport_len`, `iph_totlen`, `skb_ip_totlen`, `IP_MAX_MTU`, and `iph_set_totlen`.

## Control flow
Consumers read the IPv4 header from the skb network header, inner network header, or transport header for IP-in-IP. Length helpers decode `iph->tot_len`; for TCP GSO with a zero field they infer the effective length from `skb->len` and network offset. `iph_set_totlen` writes zero for packets exceeding the 16-bit IPv4 total length field.

## State and persistence
The header has no state. It reads and mutates only packet header fields in caller-owned skbs.

## Dependencies and integration points
It depends on `skbuff.h`, endian conversion via UAPI IP definitions, and GSO helpers. It is used across IPv4 routing, tunnels, offload, filtering, and transport code.

## Risks and test signals
Risks include stale skb header offsets, jumbo/GSO length interpretation, and misuse on non-IPv4 packets. Tests should include encapsulated packets, TCP GSO with zero total length, maximum MTU boundaries, and tunnel transport header access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ip.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ipack.h -->
# sources/distributed-fs/ceph-client/include/linux/ipack.h

## Purpose
`ipack.h` defines the IndustryPack bus framework contract for carrier boards and mezzanine drivers: device identity, address spaces, bus operations, driver registration, and carrier module reference handling.

## Important APIs, types, and functions
Key definitions include IDPROM offsets, vendor/device constants, `enum ipack_space`, `struct ipack_region`, `struct ipack_device`, `struct ipack_driver_ops`, `struct ipack_driver`, `struct ipack_bus_ops`, and `struct ipack_bus_device`. Public functions include bus, driver, and device register/unregister/add/delete/get/put helpers, plus `DEFINE_IPACK_DEVICE_TABLE`, `IPACK_DEVICE`, `ipack_get_carrier`, and `ipack_put_carrier`.

## Control flow
Carrier drivers register an `ipack_bus_device`, populate an `ipack_device` with slot and regions, call `ipack_device_init`, then add it. Mezzanine drivers register an `ipack_driver` with an ID table and probe/remove callbacks. Bus operations provide IRQ and error/clock handling while direct memory access remains carrier-specific.

## State and persistence
State lives in kernel device objects, mapped regions, parsed IDPROM fields, module references, and carrier-private bus data. No on-disk state exists.

## Dependencies and integration points
It integrates with the Linux device model, module refcounts, mod_devicetable matching, and interrupt handling.

## Risks and test signals
Risks include carrier/device lifetime bugs, IDPROM CRC or endianness mistakes, stale mapped regions, and missing module references. Tests should cover failed init/add cleanup, driver match/probe/remove, carrier unregister with devices present, IRQ request/free, and clock/error callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ipack.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ipc.h -->
# sources/distributed-fs/ceph-client/include/linux/ipc.h

## Purpose
`ipc.h` defines the in-kernel permission and lifetime object common to System V IPC objects such as semaphore arrays, message queues, and shared memory segments.

## Important APIs, types, and functions
The central type is `struct kern_ipc_perm`, containing a spinlock, deletion flag, ID/key, owner and creator credentials, mode bits, sequence number, LSM security pointer, rhashtable node, RCU head, and refcount.

## Control flow
There are no functions in this header. IPC implementations embed or reference this structure, lock it while mutating permissions/state, use the rhashtable node for key lookup, and rely on RCU/refcounting for safe teardown.

## State and persistence
State is runtime IPC object metadata. It persists only while the IPC object exists in an IPC namespace.

## Dependencies and integration points
It depends on spinlock types, kernel uid/gid wrappers, rhashtable storage, refcounts, RCU, and UAPI IPC constants. LSMs use the `security` pointer.

## Risks and test signals
Risks include sequence-number reuse, use-after-free across RCU/refcount paths, permission races after `deleted`, and credential namespace mistakes. Tests should cover create/remove races, key lookup, permission checks, LSM hooks, and object ID recycling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ipc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ipc_namespace.h -->
# sources/distributed-fs/ceph-client/include/linux/ipc_namespace.h

## Purpose
`ipc_namespace.h` defines per-namespace IPC state for SysV IPC and POSIX message queues, including object ID tables, resource limits, sysctl registration, mqueue mounts, and namespace reference management.

## Important APIs, types, and functions
Core types are `struct ipc_ids` and `struct ipc_namespace`. Exports include `init_ipc_ns`, `mq_lock`, `copy_ipcs`, `get_ipc_ns`, `get_ipc_ns_not_zero`, `put_ipc_ns`, `mq_init_ns`, sysctl setup/retire helpers, and `shm_destroy_orphaned`. It also defines POSIX mqueue defaults and hard limits.

## Control flow
Namespace creation copies or rejects IPC namespaces depending on `CLONE_NEWIPC` and configuration. SysV IPC uses `ids[3]` IDR/rhashtable sets. POSIX mqueue setup creates namespace-local defaults, sysctls, and mqueue mount state. Reference helpers increment/decrement namespace lifetime around users.

## State and persistence
State is namespace-scoped and runtime-only: IPC object IDs, sem/msg/shm counters, mqueue counts and limits, sysctl headers, mount references, owning user namespace, ucounts, and `ns_common`.

## Dependencies and integration points
It integrates namespaces, nsproxy, user namespaces, IDR, rhashtable, sysctl, percpu counters, mqueuefs, and SysV IPC implementations.

## Risks and test signals
Risks include reference underflow, mqueue counter drift, sysctl teardown races, limit enforcement errors, and forced shared-memory removal surprises. Tests should cover `CLONE_NEWIPC`, disabled feature stubs, mqueue limit sysctls, namespace teardown with live queues/segments, and checkpoint-restore `next_id`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ipc_namespace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ipmi.h -->
# sources/distributed-fs/ceph-client/include/linux/ipmi.h

## Purpose
`ipmi.h` defines the upper-layer IPMI message handler API used by kernel clients to send BMC messages, receive responses/events, watch SMI interfaces, manage source addressing, enter maintenance mode, and issue panic-time requests.

## Important APIs, types, and functions
Key types are opaque `struct ipmi_user`, `struct ipmi_recv_msg`, `struct ipmi_user_hndl`, `struct ipmi_smi_watcher`, `enum ipmi_addr_src`, `union ipmi_smi_info_union`, and `struct ipmi_smi_info`. Major APIs include user create/destroy, address/LUN setters, `ipmi_request_settime`, `ipmi_request_supply_msgs`, polling, command registration, event enabling, watcher registration, address validation, SMI info lookup, checksum, and panic request helpers.

## Control flow
Clients create a user for an interface, issue requests with message IDs and optional supplied buffers, and receive callbacks through `ipmi_recv_hndl`. Watchers are notified for new/gone SMIs. Panic and watchdog callbacks run under special constraints and must avoid normal IPMI calls where documented.

## State and persistence
Runtime state includes users, interface source addresses/LUNs, command registrations, queued receive messages, event delivery flags, watchers, and maintenance mode. No persistent storage is defined here.

## Dependencies and integration points
It depends on UAPI IPMI structures, list handling, devices, ACPI handles, procfs declarations, watchdog users, firmware update tooling, and low-level SMI drivers.

## Risks and test signals
Risks include callbacks under locks, use-after-destroy, command tuple conflicts, retry timing, panic-context allocation, and interface-wide address changes affecting all users. Tests should cover user destruction while callbacks are pending, duplicate command registration, event subscription handoff, maintenance mode transitions, supplied-message paths, and SMI watcher hotplug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ipmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ipmi_smi.h -->
# sources/distributed-fs/ceph-client/include/linux/ipmi_smi.h

## Purpose
`ipmi_smi.h` defines the low-level System Management Interface side of the IPMI stack: how KCS/SMIC/BT/platform SMI drivers register, exchange messages with the IPMI message handler, report asynchronous data, and expose device identity.

## Important APIs, types, and functions
Important definitions include `struct ipmi_smi`, watch-mask bits, `enum ipmi_smi_msg_type`, `struct ipmi_smi_msg`, `struct ipmi_smi_handlers`, `struct ipmi_device_id`, `ipmi_demangle_device_id`, `ipmi_add_smi`, `ipmi_register_smi`, `ipmi_unregister_smi`, `ipmi_smi_msg_received`, `ipmi_smi_watchdog_pretimeout`, `ipmi_alloc_smi_msg`, and `ipmi_free_smi_msg`.

## Control flow
Low-level drivers register handlers and private `send_info`, wait for `start_processing`, then accept serialized outbound messages via `sender`. They return completions or async data with `ipmi_smi_msg_received`, optionally poll, flush, enter run-to-completion mode, and toggle maintenance/watch behavior.

## State and persistence
State lives in SMI interface registration, queued `ipmi_smi_msg` objects, response buffers, watch mode, run-to-completion mode, and parsed BMC device IDs. It is runtime-only.

## Dependencies and integration points
It integrates with `ipmi.h`, IPMI message definitions, platform devices, procfs, device model, and interrupt/polling SMI drivers.

## Risks and test signals
Risks include non-failing sender contract violations, malformed Get Device ID parsing, shutdown while messages are inflight, panic polling deadlocks, and async message size errors. Tests should cover add/remove with users present, `ipmi_demangle_device_id` boundary lengths, IPMB-direct support, watchdog pretimeout delivery, and run-to-completion crash paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ipmi_smi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ipv6.h -->
# sources/distributed-fs/ceph-client/include/linux/ipv6.h

## Purpose
`ipv6.h` defines kernel IPv6 configuration, skb control-block metadata, socket private storage, and inline helpers for IPv6 header and payload length handling.

## Important APIs, types, and functions
Key items include `ipv6_optlen`, `ipv6_authlen`, `struct ipv6_devconf`, `struct ipv6_params`, `ipv6_hdr`, `inner_ipv6_hdr`, `ipipv6_hdr`, `ipv6_transport_len`, `ipv6_payload_len`, `ipv6_set_payload_len`, `struct inet6_skb_parm`, `IP6CB`, `inet6_iif`, `inet6_is_jumbogram`, `inet6_sdif`, `struct ipv6_pinfo`, raw/UDP/TCP IPv6 socket wrappers, and `inet6_sk` helpers.

## Control flow
Receive and transmit paths populate `IP6CB(skb)` with parsed extension-header offsets and flags, then socket and routing code reads per-device and per-socket IPv6 configuration. Payload helpers infer jumbo/GSO payload length when the 16-bit field is zero.

## State and persistence
State is runtime sysctl/device/socket/skb metadata: devconf knobs, stable secret, multicast lists, sticky packet info, pktoptions, PMTU notifications, and IPv6 module enable state.

## Dependencies and integration points
It depends on UAPI IPv6, cacheline grouping, TCP/UDP/inet socket types, skbuff GSO helpers, RCU socket options, sysctl, and optional IPv6 features such as MROUTE, SEG6, HMAC, optimistic DAD, and L3 master devices.

## Risks and test signals
Risks include layout changes to protocol socket wrappers, stale skb control blocks after TCP parsing, GSO/jumbogram length mistakes, per-netdev sysctl races, and optional-config stub misuse. Tests should cover extension-header parsing flags, L3 master ingress, jumbograms, IPv6-disabled builds, DAD/autoconf sysctls, and raw/UDP/TCP socket layout assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ipv6.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ipv6_route.h -->
# sources/distributed-fs/ceph-client/include/linux/ipv6_route.h

## Purpose
`ipv6_route.h` provides small kernel helpers around UAPI IPv6 route flags, mainly for extracting and decoding RFC router-preference bits.

## Important APIs, types, and functions
It defines `IPV6_EXTRACT_PREF(flag)` and `IPV6_DECODE_PREF(pref)`, using `RTF_PREF_MASK` from `uapi/linux/ipv6_route.h`.

## Control flow
Routing code masks route flags, shifts preference bits into a compact value, then XOR-decodes it into the kernel preference ordering where low, medium, and high become ordered values.

## State and persistence
The header has no state and does not persist anything.

## Dependencies and integration points
It integrates with IPv6 route table entries, router advertisements, route preference display, and UAPI route flag definitions.

## Risks and test signals
Risks are bit-position drift with UAPI flags and callers confusing encoded versus decoded preference. Tests should cover low/medium/high route preference flags and zero/default routes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ipv6_route.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irq-entry-common.h -->
# sources/distributed-fs/ceph-client/include/linux/irq-entry-common.h

## Purpose
`irq-entry-common.h` defines generic syscall/interrupt/NMI entry and exit state handling shared by architectures: lockdep IRQ state, context tracking/RCU transitions, tracing, KMSAN register cleanup, rseq notifications, deferred hrtimer rearming, and user-mode work loops.

## Important APIs, types, and functions
Important interfaces include `EXIT_TO_USER_MODE_WORK*`, architecture hooks, `enter_from_user_mode`, `exit_to_user_mode_loop`, syscall/irq exit prepare helpers, `exit_to_user_mode`, `irqentry_enter_from_user_mode`, `irqentry_exit_to_user_mode`, `irqentry_state_t`, `irqentry_enter_from_kernel_mode`, `irqentry_exit_to_kernel_mode*`, `irqentry_enter`, `irqentry_exit`, `irqentry_nmi_enter`, and `irqentry_nmi_exit`.

## Control flow
Low-level architecture entry code calls these helpers with interrupts disabled. User entries leave context tracking user state, restore lockdep/tracing, and unpoison registers. Exits process pending TIF work, validate no temporary mappings, then re-enter user tracking. Kernel entries conditionally enter/exit RCU depending on idle/EQS state and may run preempt checks before returning.

## State and persistence
State is per-CPU/per-task transient entry state: RCU watching/EQS, lockdep hardirq state, TIF work flags, rseq entry state, hrtimer deferred work, and `irqentry_state_t.exit_rcu`.

## Dependencies and integration points
It integrates with architecture `pt_regs`, context tracking, tick/nohz, lockdep, trace IRQ flags, KMSAN, rseq, static calls for preempt dynamic, and unwind state.

## Risks and test signals
Risks include wrong interrupt-disable assumptions, missing RCU transitions from idle, instrumentation in noinstr regions, unhandled TIF flags, and preempt/lockdep mismatches. Tests should include user/kernel/idle interrupt entry, NMI nesting, NO_HZ_FULL, PREEMPT_DYNAMIC, KMSAN builds, rseq exits, and hrtimer deferred rearm paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irq-entry-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irq.h -->
# sources/distributed-fs/ceph-client/include/linux/irq.h

## Purpose
`irq.h` is the central generic IRQ subsystem contract for architecture and interrupt-controller code. It defines IRQ trigger/status bits, per-IRQ data objects, `irq_chip` callbacks, generic IRQ chip helpers, descriptor allocation, flow handlers, affinity, hierarchy propagation, IPI helpers, and top-level IRQ handler registration.

## Important APIs, types, and functions
Core types include `struct irq_common_data`, `struct irq_data`, `struct irq_chip`, `struct irq_chip_regs`, `struct irq_chip_type`, `struct irq_chip_generic`, domain generic-chip info, and `struct irq_matrix`. Important APIs cover `irqd_*` accessors, built-in handlers, parent-chip helpers, `irq_set_chip_and_handler*`, status modifiers, chip/data getters, descriptor allocation/freeing, generic chip callbacks/setup, register read/write wrappers, IRQ matrix alloc/free, IPI send helpers, and `set_handle_irq`.

## Control flow
IRQ domains allocate descriptors and attach `irq_data` to chips. Flow handlers call chip callbacks for ack/mask/eoi/unmask and actions. Affinity and wake state propagate through `irq_chip` methods and, for stacked domains, parent helper functions. Generic chip setup maps register offsets and bit masks into reusable handlers.

## State and persistence
State is runtime interrupt metadata: trigger type, disabled/masked/in-progress flags, affinity masks, MSI descriptors, chip/private data, generic chip mask caches, wake state, and IRQ matrix allocations.

## Dependencies and integration points
It depends on arch IRQ headers, `irqdesc.h`, cpumasks, topology, I/O accessors, MSI, irqdomain hierarchy, SMP migration, power management, kexec, and proc/debugfs display.

## Risks and test signals
Risks include direct mutation of accessor-protected state, broken chip callback ordering, affinity migration races, stale generic-chip mask caches, hierarchy parent failures, and invalid descriptor lifetime. Tests should cover all trigger types, chained/stacked chips, managed affinity CPU hotplug, suspend/wake, MSI compose/write, IPI domains, generic-chip register access, and spurious interrupt accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irq_poll.h -->
# sources/distributed-fs/ceph-client/include/linux/irq_poll.h

## Purpose
`irq_poll.h` declares the lightweight IRQ polling abstraction for drivers that need NAPI-like deferred polling outside the networking stack.

## Important APIs, types, and functions
It defines `irq_poll_fn`, `struct irq_poll` with list, state, weight, and callback, state bits `IRQ_POLL_F_SCHED` and `IRQ_POLL_F_DISABLE`, and APIs `irq_poll_sched`, `irq_poll_init`, `irq_poll_complete`, `irq_poll_enable`, and `irq_poll_disable`.

## Control flow
Drivers initialize a poll object with weight and callback, schedule it from interrupt context, process work in the poll callback, and call complete/enable/disable as work drains or devices stop.

## State and persistence
State is runtime-only in the poll object and core poll lists. There is no persistence.

## Dependencies and integration points
It integrates with block/storage and other drivers needing interrupt mitigation, list management, and softirq-like polling infrastructure.

## Risks and test signals
Risks include scheduling after disable, failing to complete, weight starvation, and lifetime races during device removal. Tests should cover concurrent schedule/disable, callback budget exhaustion, completion rearm, and teardown with pending work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irq_poll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irq_sim.h -->
# sources/distributed-fs/ceph-client/include/linux/irq_sim.h

## Purpose
`irq_sim.h` exposes a framework for creating simulated IRQ domains whose IRQs can be requested like real interrupts and triggered from process context.

## Important APIs, types, and functions
The header defines `struct irq_sim_ops` callbacks for request/release notification and APIs `irq_domain_create_sim`, `devm_irq_domain_create_sim`, `irq_domain_create_sim_full`, `devm_irq_domain_create_sim_full`, and `irq_domain_remove_sim`.

## Control flow
Users create a firmware-node-backed simulated domain, optionally receive callbacks when simulated hwirqs are requested or released, use the IRQs through normal request/free paths, and remove the domain on teardown.

## State and persistence
State is runtime-only in the allocated irqdomain and simulator-private data pointer.

## Dependencies and integration points
It depends on the device model, fwnodes, and irqdomain core. It is useful for GPIO simulators, tests, and virtual devices.

## Risks and test signals
Risks include leaked domains, request/release callback ordering, simulated hwirq bounds, and devm cleanup mismatches. Tests should cover domain allocation failure, devm teardown, requesting every simulated IRQ, and remove while no IRQs are live.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irq_sim.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irq_work.h -->
# sources/distributed-fs/ceph-client/include/linux/irq_work.h

## Purpose
`irq_work.h` defines deferred callback work that can be queued from hard IRQ, NMI, or other atomic contexts and executed later through architecture IRQ work support.

## Important APIs, types, and functions
It provides initializers `IRQ_WORK_INIT`, `IRQ_WORK_INIT_LAZY`, `IRQ_WORK_INIT_HARD`, `DEFINE_IRQ_WORK`, `init_irq_work`, state queries `irq_work_is_pending`, `irq_work_is_busy`, `irq_work_is_hard`, queue APIs `irq_work_queue` and `irq_work_queue_on`, plus `irq_work_tick`, `irq_work_sync`, `irq_work_run`, `irq_work_needs_cpu`, `irq_work_single`, and `arch_irq_work_raise`.

## Control flow
Callers initialize a `struct irq_work`, queue it locally or to a CPU, and the architecture raises or checks IRQ work so the callback runs. `irq_work_sync` waits for busy callbacks to finish.

## State and persistence
State lives in `struct irq_work.node` atomic flags, callback pointer, and `rcuwait`; it is runtime-only.

## Dependencies and integration points
It depends on `irq_work_types.h`, SMP call-single infrastructure, RCU wait, and architecture `asm/irq_work.h` support.

## Risks and test signals
Risks include requeueing while pending/busy, missing CPU wakeups for lazy work, teardown without sync, and config stubs hiding missing callbacks. Tests should cover hard/lazy work, cross-CPU queueing, NMI-safe queueing, sync during callback, and disabled `CONFIG_IRQ_WORK` builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irq_work.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irq_work_types.h -->
# sources/distributed-fs/ceph-client/include/linux/irq_work_types.h

## Purpose
`irq_work_types.h` isolates the `struct irq_work` layout so low-level headers can use the type without pulling in full IRQ work APIs.

## Important APIs, types, and functions
It defines `struct irq_work` with a `struct __call_single_node`, callback function pointer, and `struct rcuwait`.

## Control flow
There are no functions. Other headers initialize, queue, inspect, and synchronize this structure.

## State and persistence
State is per-work-item runtime state encoded in call-single flags and wait state. Nothing persists.

## Dependencies and integration points
It depends on SMP call-single types and generic integer types, and is consumed by `irq_work.h`, tracing, scheduler, and RCU-adjacent code.

## Risks and test signals
Risks are ABI/layout assumptions by low-level code and improper zeroing or copying of live work items. Tests should focus on initialization macros, sync behavior, and compile coverage in architecture headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irq_work_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irqbypass.h -->
# sources/distributed-fs/ceph-client/include/linux/irqbypass.h

## Purpose
`irqbypass.h` declares the IRQ bypass manager used to pair interrupt producers, such as assigned physical-device IRQs, with consumers, such as virtualization hardware, using a shared `eventfd_ctx` so delivery can be offloaded or bypass host handling.

## Important APIs, types, and functions
Core types are `struct irq_bypass_producer` and `struct irq_bypass_consumer`, with eventfd, peer pointer, callbacks for add/delete, and optional stop/start hooks. APIs are producer and consumer register/unregister functions.

## Control flow
Producers and consumers register independently. The manager matches unique eventfds, quiesces each side with `stop`, connects them through add callbacks, then restarts them. Unregistering reverses this through delete callbacks.

## State and persistence
State is runtime pairing metadata in registered producer/consumer structures and manager lists. No persistent state exists.

## Dependencies and integration points
It depends on list infrastructure and `eventfd_ctx`, and integrates with KVM/VFIO/MSI interrupt paths.

## Risks and test signals
Risks include non-unique eventfds, callback ordering failures, unregister races, and stale peer pointers. Tests should cover register order permutations, add callback failure, unregister while paired, duplicate eventfds, and stop/start ordering under concurrent VM/device teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irqbypass.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irqchip.h -->
# sources/distributed-fs/ceph-client/include/linux/irqchip.h

## Purpose
`irqchip.h` provides declaration macros and probe glue for interrupt-controller drivers discovered by Device Tree, ACPI MADT subtables, or platform driver matching.

## Important APIs, types, and functions
It defines `platform_irq_probe_t`, typecheck sentinels, `IRQCHIP_DECLARE`, `platform_irqchip_probe`, `IRQCHIP_PLATFORM_DRIVER_BEGIN`, `IRQCHIP_MATCH`, `IRQCHIP_PLATFORM_DRIVER_END`, `IRQCHIP_ACPI_DECLARE`, and `irqchip_init`.

## Control flow
Built-in irqchip drivers declare compatible strings and init/probe callbacks. Early DT init uses `OF_DECLARE_2`; platform-driver macros build a suppressed-bind-attrs platform driver; ACPI declarations register MADT subtable probes. `irqchip_init` is compiled out when irqchip support is disabled.

## State and persistence
The header creates static match/probe metadata through macros. Runtime state is owned by individual irqchip drivers.

## Dependencies and integration points
It integrates with ACPI, OF, platform devices, module tables, built-in platform drivers, and core irqchip initialization.

## Risks and test signals
Risks include wrong callback signature, duplicate declaration names, missing module match tables, and platform probe disabled by config. Tests should compile DT/ACPI/platform irqchip variants and boot-probe controllers from each discovery path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irqchip.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irqchip/arm-gic-common.h -->
# sources/distributed-fs/ceph-client/include/linux/irqchip/arm-gic-common.h

## Purpose
`arm-gic-common.h` holds shared ARM GIC constants and declarations used by multiple GIC versions, currently default interrupt priority and GICv2m MSI initialization.

## Important APIs, types, and functions
It defines `GICD_INT_DEF_PRI` and declares `gicv2m_init(struct fwnode_handle *parent_handle, struct irq_domain *parent)`.

## Control flow
GIC drivers include this header to use a common distributor priority and to initialize GICv2m MSI frames under a parent irqdomain.

## State and persistence
No state is defined in the header.

## Dependencies and integration points
It includes `arm-vgic-info.h` and forward-declares irqdomain/fwnode types. It integrates GIC interrupt controllers with MSI child domains and KVM VGIC metadata.

## Risks and test signals
Risks include priority mismatches across GIC versions and failed GICv2m child-domain setup. Tests should cover GICv2m probing from DT/ACPI, MSI allocation under a GIC parent, and priority programming consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irqchip/arm-gic-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irqchip/arm-gic-v3-prio.h -->
# sources/distributed-fs/ceph-client/include/linux/irqchip/arm-gic-v3-prio.h

## Purpose
`arm-gic-v3-prio.h` defines priority mask values for GICv3 IRQs and pseudo-NMIs as seen through PMR/RPR, including translation validation for the non-secure priority view.

## Important APIs, types, and functions
It defines `GICV3_PRIO_UNMASKED`, `GICV3_PRIO_IRQ`, `GICV3_PRIO_NMI`, `GICV3_PRIO_PSR_I_SET`, conversion macros, and static assertions validating ordering and non-secure round trips.

## Control flow
Architecture IRQ masking code writes these values to PMR, optionally using `GICV3_PRIO_PSR_I_SET` when sections must rely on `PSR.I` rather than priority masking.

## State and persistence
No runtime state is declared.

## Dependencies and integration points
It is shared by GICv3 driver and arm64 entry/interrupt masking code, including pseudo-NMI support.

## Risks and test signals
Risks include invalid values under the NS priority transform and breaking pseudo-NMI ordering. Tests should cover compile-time assertions, IRQ/NMI masking behavior, and arm64 paths that temporarily force `PSR.I`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irqchip/arm-gic-v3-prio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irqchip/arm-gic-v3.h -->
# sources/distributed-fs/ceph-client/include/linux/irqchip/arm-gic-v3.h

## Purpose
`arm-gic-v3.h` is the architectural register and data-structure contract for ARM GICv3/GICv4 interrupt controllers, redistributors, ITS/LPI support, virtual LPIs, and CPU interface system registers.

## Important APIs, types, and functions
It defines distributor, redistributor, VLPI, ITS, command, error, and CPU-interface register offsets and bitfields; cacheability/shareability encoders; `GIC_IRQ_TYPE_LPI`; `struct rdists`; and declarations for ITS/LPI/MBI initialization. `gic_enable_sre` enables the system-register interface using arch `gic_read_sre`/`gic_write_sre`.

## Control flow
GIC drivers program distributor/redistributor control, route SPIs/PPIs/LPIs, allocate and configure LPI property/pending tables, issue ITS commands, and enable CPU interface system-register access. Virtualization paths use VPROPBASER/VPENDBASER/VSGI fields for vLPI/vSGI state.

## State and persistence
State is hardware register and table state plus runtime `rdists` tracking: per-CPU redistributor base, pending page, physical base, property table, GIC typer fields, VLPI capability flags, and memory reservation hotplug state.

## Dependencies and integration points
It depends on bitfield macros, arch GICv3 system-register access, irqdomains, fwnodes, page allocation, KVM VGIC, MSI/ITS code, and CPU hotplug.

## Risks and test signals
Risks include wrong bitfield encoding, cacheability/shareability mismatches, ITS command-table sizing, redistributor affinity discovery, SRE enable failure, and virtual LPI residency bugs. Tests should cover GICv3/v4 hardware, ITS MSI allocation, LPI table invalidation, CPU hotplug, pseudo-NMI priority, KVM vLPI/vSGI paths, and emulated GIC register behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irqchip/arm-gic-v3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irqchip/arm-gic-v4.h -->
# sources/distributed-fs/ceph-client/include/linux/irqchip/arm-gic-v4.h

## Purpose
`arm-gic-v4.h` defines the Linux/KVM-facing structures and APIs for GICv4 virtual LPIs, virtual processing elements, doorbells, and vSGI/vPE management.

## Important APIs, types, and functions
Important types include `struct its_vm`, `struct its_vpe`, `struct its_vlpi_map`, `enum its_vcpu_info_cmd_type`, and `struct its_cmd_info`. APIs include vCPU IRQ allocation/free, VPE resident/nonresident/commit/invalidate operations, VLPI map/get/unmap/property update, vSGI property update, `its_init_v4`, and `gic_cpuif_has_vsgi`.

## Control flow
KVM embeds VM/VPE structures, allocates doorbell LPIs, maps physical IRQs to VLPIs through `irq_set_vcpu_affinity` command info, schedules VPEs resident/nonresident around vCPU execution, and updates virtual interrupt properties or invalidates state through ITS commands.

## State and persistence
Runtime state includes VM fwnode/domain, virtual property page, VPE array, doorbell bitmap/counts, per-VPE VPT page, residency/ready flags, VLPI counts, vSGI config, collection ID, and locks for VMAPP/VPE/VMOVP ordering.

## Dependencies and integration points
It integrates KVM, GICv3 ITS, irqdomain ops, raw spinlocks, pages, and virtual interrupt affinity APIs.

## Risks and test signals
Risks include lock-order violations, stale VPE residency, doorbell LPI leaks, property-update races, and GICv4.0/v4.1 union misuse. Tests should cover VM create/destroy, vCPU schedule/deschedule, VLPI map/unmap under load, vSGI injection, doorbell enable/disable, and CPU migration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irqchip/arm-gic-v4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irqchip/arm-gic-v5.h -->
# sources/distributed-fs/ceph-client/include/linux/irqchip/arm-gic-v5.h

## Purpose
`arm-gic-v5.h` defines the emerging ARM GICv5 register, table, global-state, and helper interfaces for IRS, ITS, IWB, PPIs/SPIs/LPIs/IPIs, and virtualization-capable interrupt routing.

## Important APIs, types, and functions
It defines INTID/hwirq type fields, architected PPI IDs, table attribute encodings, IRS/ITS/IWB register offsets and bitfields, table entry layouts, `struct gicv5_chip_data`, `struct gicv5_irs_chip_data`, wait helpers `gicv5_wait_for_op*_s`, probe/init/remove functions for IRS/ITS/LPI domains, SPI type setting, IAFFID lookup, and config structures for VPE, dev tables, and ITTs.

## Control flow
GICv5 code probes IRS and ITS instances from firmware, configures global domains, allocates interrupt state tables, maps SPIs to IRS ranges, initializes LPIs, waits for register operations to become idle, and exposes virtualization state through VPE/table structures.

## State and persistence
State is runtime hardware configuration: global domains, SPI counts, CPU/IRS priority and ID widths, IRS list entries, LPI/IST/ITT/devtab memory, SPI config locks, and VPE residency flags.

## Dependencies and integration points
It depends on I/O polling, cache flushing, SMP/sysreg arch headers, irqdomains, fwnodes, ACPI/OF probing, KVM, and LPI/MSI management.

## Risks and test signals
Risks include timeout logic, new bitfield/table encoding errors, wrong page-size support selection, IAFFID mapping mistakes, SPI range overlap, and virtualization table lifetime bugs. Tests should cover OF and ACPI probe, IRS enable/remove, LPI init/deinit, SPI type programming, timeout paths, CPU registration, and table invalidation/sync.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irqchip/arm-gic-v5.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irqchip/arm-gic.h -->
# sources/distributed-fs/ceph-client/include/linux/irqchip/arm-gic.h

## Purpose
`arm-gic.h` defines ARM GICv1/v2 distributor, CPU interface, virtualization control, list-register, and VM control register constants, plus driver hooks for cascaded/child GICs, save/restore, SGIs, and CPU target migration.

## Important APIs, types, and functions
It defines `GIC_CPU_*`, `GIC_DIST_*`, `GICC_*`, `GICD_*`, `GICH_*`, `GICH_LR_*`, `GICH_VMCR_*`, `GICV_*` macros and functions such as `gic_cascade_irq`, `gic_cpu_if_down`, CPU/distributor save/restore, `gic_of_init`, `gic_of_init_child`, `gic_send_sgi`, `gic_get_cpu_id`, `gic_migrate_target`, and `gic_get_sgir_physaddr`.

## Control flow
Drivers program distributor enable/pending/active/priority/target/config registers, use CPU interface IAR/EOI/deactivate paths, optionally cascade child controllers, save/restore state over PM, and send SGIs for IPIs.

## State and persistence
State is mostly hardware register state; driver-owned `struct gic_chip_data` is forward-declared. Save/restore helpers preserve CPU and distributor state across suspend.

## Dependencies and integration points
It integrates with irqdomains, DT probing, ARM interrupt entry, KVM GICv2 emulation, CPU hotplug, and SMP IPI routing.

## Risks and test signals
Risks include register offset misuse, SGI target migration bugs, virtualization LR/VMCR bit errors, and suspend restore ordering. Tests should cover GICv2 boot, child GIC probing, SGI send, CPU hotplug, suspend/resume, and KVM maintenance interrupt paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irqchip/arm-gic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irqchip/arm-vgic-info.h -->
# sources/distributed-fs/ceph-client/include/linux/irqchip/arm-vgic-info.h

## Purpose
`arm-vgic-info.h` carries interrupt-controller metadata from physical GIC drivers to KVM VGIC initialization code.

## Important APIs, types, and functions
It defines `enum gic_type`, `struct gic_kvm_info`, and `vgic_set_kvm_info` with a no-op stub when KVM is disabled.

## Control flow
GIC drivers populate virtual CPU/control interface resources, maintenance IRQ, hardware deactivation quirks, and v4/v4.1 capability flags, then pass them to KVM through `vgic_set_kvm_info`.

## State and persistence
The header declares only transfer metadata; KVM stores any accepted copy at runtime.

## Dependencies and integration points
It depends on resource and I/O types and integrates GICv2/v3/v5 drivers with KVM ARM VGIC.

## Risks and test signals
Risks include incorrect maintenance IRQ masking, wrong resource ranges, misreported vLPI/RVPEID capability, and KVM disabled stubs hiding unused data. Tests should cover KVM boot on GICv2/v3/v5, v4/v4.1 capability exposure, and platforms with no maintenance IRQ mask.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irqchip/arm-vgic-info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irqchip/arm-vic.h -->
# sources/distributed-fs/ceph-client/include/linux/irqchip/arm-vic.h

## Purpose
`arm-vic.h` declares legacy ARM VIC initialization for non-DT or early platform code.

## Important APIs, types, and functions
It declares `vic_init(void __iomem *base, unsigned int irq_start, u32 vic_sources, u32 resume_sources)`.

## Control flow
Board code maps the VIC base, chooses the Linux IRQ base and source masks, then calls `vic_init` to register and configure the controller.

## State and persistence
State is in hardware registers and generic IRQ descriptors initialized by the VIC implementation. Resume source state supports PM restoration.

## Dependencies and integration points
It depends on MMIO types and integrates legacy ARM platforms with generic IRQ descriptors.

## Risks and test signals
Risks include wrong MMIO base, IRQ range collisions, and resume-source mask mistakes. Tests should boot legacy VIC boards and exercise suspend/resume and each IRQ source.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irqchip/arm-vic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irqchip/chained_irq.h -->
# sources/distributed-fs/ceph-client/include/linux/irqchip/chained_irq.h

## Purpose
`chained_irq.h` provides common entry and exit helpers for chained interrupt handlers whose parent chip may use either fasteoi or level-triggered mask/ack flow control.

## Important APIs, types, and functions
It defines `chained_irq_enter(struct irq_chip *chip, struct irq_desc *desc)` and `chained_irq_exit(struct irq_chip *chip, struct irq_desc *desc)`.

## Control flow
On entry, FastEOI chips need no action. Other chips use `irq_mask_ack` if available, otherwise mask then ack. On exit, FastEOI chips call `irq_eoi`; other chips unmask the parent line.

## State and persistence
No state is owned by the header; it mutates parent IRQ chip hardware state through callbacks.

## Dependencies and integration points
It depends on `linux/irq.h` and is used by GPIO and secondary interrupt controllers chained under a parent IRQ.

## Risks and test signals
Risks include passing a chip lacking needed callbacks, double masking/eoi, and wrong parent descriptor. Tests should cover fasteoi and level parent chips, nested child interrupt storms, and teardown while the chained line is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irqchip/chained_irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irqchip/irq-bcm2836.h -->
# sources/distributed-fs/ceph-client/include/linux/irqchip/irq-bcm2836.h

## Purpose
`irq-bcm2836.h` defines register offsets and local interrupt IDs for the BCM2836/Raspberry Pi 2 root local interrupt controller.

## Important APIs, types, and functions
It defines local control/prescaler/GPU routing/PM routing/timer/mailbox status and set/clear offsets, plus IRQ numbers for physical/virtual timers, mailboxes, GPU fast IRQ, PMU fast IRQ, and `LAST_IRQ`.

## Control flow
The BCM2836 irqchip driver writes routing and enable registers, reads per-CPU pending registers, uses mailbox set/clear registers for IPIs, and maps the local IRQ IDs into the generic IRQ domain.

## State and persistence
State is hardware register state for per-CPU local routing, timer/mailbox enables, pending bits, and mailbox latches.

## Dependencies and integration points
It integrates Raspberry Pi local interrupts with ARM timer, PMU, GPU interrupt routing, SMP IPIs, and generic IRQ domains.

## Risks and test signals
Risks include CPU/mailbox bit indexing errors, FIQ overriding IRQ routing, and stale mailbox bits. Tests should cover timer interrupts on each CPU, IPIs via mailbox 0, PMU routing, GPU fast IRQ routing, and SMP boot/hotplug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irqchip/irq-bcm2836.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irqchip/irq-madera.h -->
# sources/distributed-fs/ceph-client/include/linux/irqchip/irq-madera.h

## Purpose
`irq-madera.h` enumerates Cirrus Logic Madera codec interrupt lines and provides wrapper helpers for child MFD drivers to map, request, free, and configure wake for those interrupts.

## Important APIs, types, and functions
It defines `MADERA_IRQ_*` IDs for clocks, jack/mic detection, DSPs, headphone/speaker faults and enable-done events, GPIOs, and bus errors, plus `MADERA_NUM_IRQ`. Helpers are `madera_get_irq_mapping`, `madera_request_irq`, `madera_free_irq`, and `madera_set_irq_wake`.

## Control flow
Child drivers pass a Madera-local IRQ number. The helpers ensure an IRQ device exists, translate through `regmap_irq_get_virq`, and call generic `request_threaded_irq`, `free_irq`, or `irq_set_irq_wake`.

## State and persistence
State lives in the parent `struct madera`: IRQ device presence and regmap IRQ data. The header has no independent state.

## Dependencies and integration points
It depends on the Madera MFD core, regmap IRQ, and threaded IRQ APIs. It integrates codec subdrivers with a shared parent interrupt controller.

## Risks and test signals
Risks include stale or absent `irq_dev`, wrong local IRQ IDs, ONESHOT handler expectations, and wake configuration on unmapped IRQs. Tests should cover each child requesting/freeing IRQs, parent probe failure, wake enable/disable, and IRQ delivery for jack, DSP, GPIO, and fault events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irqchip/irq-madera.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irqchip/irq-msi-lib.h -->
# sources/distributed-fs/ceph-client/include/linux/irqchip/irq-msi-lib.h

## Purpose
`irq-msi-lib.h` provides shared helpers for irqchip drivers that expose MSI-capable domains and need common bus-token selection and MSI domain-info initialization.

## Important APIs, types, and functions
It defines `MATCH_PCI_MSI` when PCI MSI is enabled, `MATCH_PLATFORM_MSI`, and declares `msi_lib_irq_domain_select` and `msi_lib_init_dev_msi_info`.

## Control flow
IRQ domain `select` callbacks can delegate bus-token matching to `msi_lib_irq_domain_select`. Device MSI setup uses `msi_lib_init_dev_msi_info` to populate `struct msi_domain_info` against a real parent domain.

## State and persistence
No state is declared in the header; MSI domain state is owned by irqdomain/MSI core and drivers.

## Dependencies and integration points
It depends on bit operations, irqdomain, and MSI core. It integrates irqchips with PCI and platform MSI buses.

## Risks and test signals
Risks include wrong bus-token masks when PCI MSI is disabled, mismatched parent domains, and incomplete MSI info initialization. Tests should cover PCI MSI, platform MSI, disabled PCI MSI builds, and domain selection with multiple MSI domains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irqchip/irq-msi-lib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irqchip/irq-omap-intc.h -->
# sources/distributed-fs/ceph-client/include/linux/irqchip/irq-omap-intc.h

## Purpose
`irq-omap-intc.h` declares OMAP interrupt controller hooks used by platform idle and suspend code.

## Important APIs, types, and functions
It declares `omap_irq_pending`, `omap_intc_save_context`, `omap_intc_restore_context`, `omap3_intc_suspend`, `omap3_intc_prepare_idle`, and `omap3_intc_resume_idle`.

## Control flow
OMAP PM code can check pending IRQs before idle, save/restore controller context over suspend, and run OMAP3-specific idle preparation/resume sequences.

## State and persistence
State is hardware interrupt controller context saved by the implementation and restored after low-power states.

## Dependencies and integration points
It integrates OMAP irqchip code with SoC idle, suspend, and wakeup paths.

## Risks and test signals
Risks include missed pending interrupts before idle, incomplete context restore, and suspend/resume ordering errors. Tests should cover idle entry/exit, wake sources, system suspend, and pending interrupt races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irqchip/irq-omap-intc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irqchip/irq-renesas-rzt2h.h -->
# sources/distributed-fs/ceph-client/include/linux/irqchip/irq-renesas-rzt2h.h

## Purpose
`irq-renesas-rzt2h.h` exposes Renesas RZ/T2H ICU support for registering DMAC request-number routing from client drivers.

## Important APIs, types, and functions
It defines `RZT2H_ICU_DMAC_REQ_NO_DEFAULT` and conditionally declares `rzt2h_icu_register_dma_req`, with a no-op stub when `CONFIG_RENESAS_RZT2H_ICU` is disabled.

## Control flow
DMAC or peripheral setup code passes the ICU platform device, DMAC index/channel, and request number so the ICU implementation can program routing.

## State and persistence
State is in ICU hardware routing registers and driver-private tables; disabled builds keep none.

## Dependencies and integration points
It depends on platform devices and integrates Renesas ICU interrupt/request routing with DMAC channels.

## Risks and test signals
Risks include no-op behavior in disabled builds, invalid channel/index values, and wrong default request number. Tests should cover enabled/disabled configs, each DMAC channel mapping, and reset/default routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irqchip/irq-renesas-rzt2h.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irqchip/irq-renesas-rzv2h.h -->
# sources/distributed-fs/ceph-client/include/linux/irqchip/irq-renesas-rzv2h.h

## Purpose
`irq-renesas-rzv2h.h` exposes Renesas RZ/V2H(P) ICU support for registering DMAC request-number routing.

## Important APIs, types, and functions
It defines `RZV2H_ICU_DMAC_REQ_NO_DEFAULT` and conditionally declares `rzv2h_icu_register_dma_req`, with a no-op stub when `CONFIG_RENESAS_RZV2H_ICU` is disabled.

## Control flow
Client code tells the ICU driver which DMAC index/channel should receive a given request number. The ICU implementation owns hardware programming.

## State and persistence
State is runtime hardware/request routing; no header-owned state exists.

## Dependencies and integration points
It depends on platform devices and integrates Renesas ICU and DMA request routing for RZ/V2H(P) SoCs.

## Risks and test signals
Risks include disabled-config silent no-op, platform-device mismatch, and incorrect request/channel encoding. Tests should cover valid and default request values, all channels, disabled build coverage, and DMA functionality after ICU setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irqchip/irq-renesas-rzv2h.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irqchip/irq-sa11x0.h -->
# sources/distributed-fs/ceph-client/include/linux/irqchip/irq-sa11x0.h

## Purpose
`irq-sa11x0.h` declares legacy SA-11x0 interrupt initialization for non-DT platforms.

## Important APIs, types, and functions
It declares `sa11x0_init_irq_nodt(int irq_start, resource_size_t io_start)`.

## Control flow
Platform code calls the init function with an IRQ base and MMIO start address so the SA-11x0 interrupt controller can initialize descriptors and hardware.

## State and persistence
State is hardware register configuration and generic IRQ descriptor mappings established by the implementation.

## Dependencies and integration points
It integrates ARM SA-11x0 board files with generic IRQ handling and low-level MMIO resources.

## Risks and test signals
Risks include wrong IO start address, IRQ base collisions, and missing legacy init. Tests should boot SA-11x0 board configurations and trigger each interrupt source.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irqchip/irq-sa11x0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irqchip/riscv-aplic.h -->
# sources/distributed-fs/ceph-client/include/linux/irqchip/riscv-aplic.h

## Purpose
`riscv-aplic.h` defines the RISC-V Advanced Platform-Level Interrupt Controller register map, source modes, MSI target encoding, IDC registers, and limits.

## Important APIs, types, and functions
It defines APLIC limits, domain configuration bits, source configuration fields, M/S-mode MSI config registers and shifts, pending/enable set/clear offsets, MSI generation and target fields, IDC offsets, and TOPI/CLAIMI encoding macros.

## Control flow
The APLIC driver configures domain mode and endianness, programs each source as edge/level/detached, sets or clears pending/enable bits, routes interrupts either through direct IDC delivery or MSI target fields, and claims top pending interrupts through IDC registers.

## State and persistence
State is hardware register state for interrupt sources, pending/enabled bits, MSI address configuration, target priority/guest/hart routing, and IDC delivery/threshold.

## Dependencies and integration points
It depends on bitops and integrates RISC-V platform interrupt delivery with IMSIC/MSI mode, direct IDC mode, irqdomains, and privilege-mode-specific configuration.

## Risks and test signals
Risks include M-mode versus S-mode register selection, source ID bounds, endian set-pending offsets, target-field bit errors, and direct/MSI mode confusion. Tests should cover edge and level sources, enable/disable/pending clear, MSI target programming with IMSIC, direct IDC claim, and big-endian register paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irqchip/riscv-aplic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irqchip/riscv-imsic.h -->
# sources/distributed-fs/ceph-client/include/linux/irqchip/riscv-imsic.h

## Purpose
`riscv-imsic.h` defines the RISC-V Incoming MSI Controller register IDs, MMIO page layout, global/local configuration structures, and ACPI/firmware helper declarations.

## Important APIs, types, and functions
It defines IMSIC MMIO constants, interrupt ID ranges, CSR register numbers for delivery/threshold/pending/enable arrays, `struct imsic_local_config`, `struct imsic_global_config`, `imsic_get_global_config`, `imsic_platform_acpi_probe`, and `imsic_acpi_get_fwnode` stubs.

## Control flow
Firmware/probe code fills global target-address geometry and per-CPU MSI addresses. APLIC/MSI code queries `imsic_get_global_config` to generate MSI addresses and interrupt IDs. ACPI helpers provide fwnodes when both ACPI and IMSIC are enabled.

## State and persistence
State is runtime controller configuration: base address, guest/hart/group index widths, number of IDs and guest files, and per-CPU MSI physical/virtual addresses.

## Dependencies and integration points
It depends on devices, fwnodes, bitops, and RISC-V IMSIC config. It integrates APLIC MSI mode, irqdomains, ACPI probing, and per-CPU interrupt files.

## Risks and test signals
Risks include invalid address-geometry fields, ID range overflow, missing per-CPU local config, disabled-config NULL global config, and ACPI fwnode mismatch. Tests should cover DT and ACPI systems, per-CPU MSI delivery, guest interrupt files, boundary IDs, and disabled IMSIC builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irqchip/riscv-imsic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irqchip/xtensa-mx.h -->
# sources/distributed-fs/ceph-client/include/linux/irqchip/xtensa-mx.h

## Purpose
`xtensa-mx.h` declares legacy initialization for the Xtensa MX interrupt distributor.

## Important APIs, types, and functions
It forward-declares `struct device_node` and declares `xtensa_mx_init_legacy(struct device_node *interrupt_parent)`.

## Control flow
Legacy Xtensa platform code calls the initializer with the parent interrupt-controller node to register MX distribution behavior.

## State and persistence
State is owned by the Xtensa MX irqchip implementation and generic IRQ domains/descriptors.

## Dependencies and integration points
It integrates Xtensa legacy interrupt setup with firmware nodes and parent controllers.

## Risks and test signals
Risks include missing parent node, wrong legacy ordering, and IRQ domain mismatches. Tests should boot Xtensa MX configurations and verify child interrupt delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irqchip/xtensa-mx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irqchip/xtensa-pic.h -->
# sources/distributed-fs/ceph-client/include/linux/irqchip/xtensa-pic.h

## Purpose
`xtensa-pic.h` declares legacy initialization for the built-in Xtensa programmable interrupt controller.

## Important APIs, types, and functions
It forward-declares `struct device_node` and declares `xtensa_pic_init_legacy(struct device_node *interrupt_parent)`.

## Control flow
Xtensa platform setup invokes the initializer to register the built-in PIC against an optional parent node before normal IRQ handling begins.

## State and persistence
Runtime state is in the PIC implementation and generic IRQ descriptors/domains.

## Dependencies and integration points
It integrates Xtensa architecture interrupt setup with generic irqchip initialization.

## Risks and test signals
Risks include wrong parent relationship, legacy init running too late, and interrupt number mapping errors. Tests should cover Xtensa PIC boot, timer IRQ delivery, and nested/parented configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irqchip/xtensa-pic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irqdesc.h -->
# sources/distributed-fs/ceph-client/include/linux/irqdesc.h

## Purpose
`irqdesc.h` defines the generic IRQ descriptor structure and descriptor-level helpers used by core IRQ handling, statistics, proc/debugfs/sysfs exposure, action lists, threaded IRQ synchronization, and mapping hardware interrupts to flow handlers.

## Important APIs, types, and functions
Important types include `struct irqstat`, `struct irq_redirect`, and `struct irq_desc`. Helpers include sparse IRQ locking, `irq_desc_kstat_cpu`, `irq_data_to_desc`, descriptor getters, `generic_handle_irq_desc`, `handle_irq_desc`, `generic_handle_irq*`, domain handle helpers, `irq_desc_has_action`, locked handler/chip setters, status checks, balancing/percpu predicates, and lockdep-class setup.

## Control flow
Architecture or domain code resolves an IRQ descriptor and invokes its `handle_irq`. Flow handlers inspect descriptor state, call actions, update stats, coordinate threaded handlers, and use locks. Domain helpers translate hwirq to desc before dispatch.

## State and persistence
Descriptor state includes common/chip data, stats, flow handler, actions, status bits, disable/wake depth, spurious counters, locks, percpu enable masks, affinity hints, pending masks, threaded IRQ bookkeeping, proc/debugfs/sysfs nodes, parent IRQ, owner, and software resend node.

## Dependencies and integration points
It depends on irq work, kobjects, mutexes, RCU, generic IRQ domains, proc/debugfs, sparse IRQ, SMP affinity, PM sleep, and lockdep.

## Risks and test signals
Risks include descriptor lifetime races under sparse IRQ, action teardown while handlers run, stats drift, wrong locked setter use, threaded IRQ synchronization bugs, and proc/debugfs stale entries. Tests should cover request/free races, generic/domain dispatch, threaded oneshot handlers, sparse descriptor allocation/free, CPU affinity changes, and PM suspend counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irqdesc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irqdomain.h -->
# sources/distributed-fs/ceph-client/include/linux/irqdomain.h

## Purpose
`irqdomain.h` defines the hardware-to-Linux IRQ translation framework: firmware specs, domain creation/removal, reverse maps, legacy/linear/tree/nomap/hierarchical domains, mapping allocation, stock translators, IPI reservations, MSI/wired helpers, and generic-chip integration.

## Important APIs, types, and functions
Key types are `struct irq_fwspec`, `struct irq_fwspec_info`, `struct irq_domain_ops`, `struct irq_domain`, and `struct irq_domain_info`. APIs include fwnode allocation/free, `irq_domain_instantiate`, devm/simple/legacy/linear/tree/hierarchy creators, domain finders, mapping create/dispose/resolve helpers, stock xlate/translate functions, `irq_domain_set_info`, hierarchical alloc/free/activate/deactivate/push/pop/parent helpers, IPI reserve/destroy, and MSI wired helpers.

## Control flow
Firmware supplies interrupt specifiers. Domain ops match/select, translate hwirqs/types, map descriptors, allocate/free hierarchical IRQs, and activate/deactivate hardware. Reverse maps use linear arrays or radix trees to resolve hwirq to descriptor/virq during interrupt dispatch.

## State and persistence
Runtime state includes domain list links, fwnode, bus token, flags, mapcount, root mutex, parent, MSI parent ops, host data, generic chips, PM device, hwirq limits, radix reverse map, and appended linear revmap.

## Dependencies and integration points
It depends on OF/fwnode, mutexes, radix trees, irq chips/data/descriptors, generic MSI, generic chips, and device-managed resources. It is the core integration layer for irqchips, GPIO, MSI, IPIs, and firmware descriptions.

## Risks and test signals
Risks include duplicate fwnode/bus-token domains, reverse-map leaks, hierarchy parent allocation rollback, wrong trigger translation, stale fwnodes, and no-map/direct-map misuse. Tests should cover each domain type, DT/ACPI fwspec translation, mapping create/dispose races, hierarchical MSI allocation, IPI domains, generic chip removal, and disabled `CONFIG_IRQ_DOMAIN` stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irqdomain.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irqdomain_defs.h -->
# sources/distributed-fs/ceph-client/include/linux/irqdomain_defs.h

## Purpose
`irqdomain_defs.h` defines bus-token values used to disambiguate multiple IRQ domains that share the same firmware node but serve different interrupt buses.

## Important APIs, types, and functions
It defines `enum irq_domain_bus_token`, including wired IRQs, generic/PCI/platform/device MSI, nexus, IPI, wakeup, VMD, DMAR, AMDVI, and wired-to-MSI domains.

## Control flow
Domain lookup and selection code compares a firmware node plus bus token to choose the correct domain for a device interrupt specifier.

## State and persistence
No runtime state is declared.

## Dependencies and integration points
It is consumed by irqdomain core, MSI code, PCI/platform/device IRQ setup, IOMMU interrupt remapping domains, and wakeup domains.

## Risks and test signals
Risks include selecting `DOMAIN_BUS_ANY` when a specific token is required and collisions between MSI domain types. Tests should cover systems with multiple domains on one fwnode, PCI MSI/MSI-X, platform MSI, and interrupt remapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irqdomain_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irqflags.h -->
# sources/distributed-fs/ceph-client/include/linux/irqflags.h

## Purpose
`irqflags.h` wraps architecture local IRQ flag operations with lockdep, tracing, debug checks, critical timing, hrtimer/posix timer/irq_work context markers, and scoped cleanup guards.

## Important APIs, types, and functions
It declares or stubs lockdep hard/soft IRQ helpers, trace IRQ flag helpers, per-CPU trace state, hardirq enter/exit/threaded markers, timer/irq_work lockdep context helpers, raw `local_irq_*` wrappers, traced `local_irq_*` wrappers, `safe_halt`, `irqs_disabled`, `irqs_disabled_flags`, and `DEFINE_LOCK_GUARD_0` guards for `irq` and `irqsave`.

## Control flow
Callers save/disable/restore/enable IRQs. With tracing enabled, wrappers record transitions only when state changes, then call raw arch operations. Debug restore checks catch bogus restores. Lockdep context helpers mark whether callbacks run as hardirq-like or softirq-like contexts.

## State and persistence
State is per-CPU hardirq trace counters and per-task softirq/irq_config trace fields. There is no persistent state.

## Dependencies and integration points
It depends on arch IRQ flag primitives, percpu access, type checking, cleanup guards, lockdep, IRQ flag tracing, preempt/irqsoff tracers, and debug IRQ flags.

## Risks and test signals
Risks include trace state diverging from hardware IRQ flags, bogus restore warnings, PREEMPT_RT softirq-context differences, and using raw APIs where traced APIs are required. Tests should cover trace-enabled/disabled builds, lockdep IRQ state, nested save/restore, safe halt, timer/irq_work context markers, and scoped guard cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irqflags.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irqflags_types.h -->
# sources/distributed-fs/ceph-client/include/linux/irqflags_types.h

## Purpose
`irqflags_types.h` isolates per-task IRQ trace event storage used when IRQ flag tracing is enabled.

## Important APIs, types, and functions
Under `CONFIG_TRACE_IRQFLAGS`, it defines `struct irqtrace_events` with counters, instruction pointers, and event IDs for hardirq and softirq enable/disable transitions.

## Control flow
The tracing/lockdep infrastructure updates this structure when IRQ state transitions occur, allowing diagnostics to report where IRQs were enabled or disabled.

## State and persistence
State is per-task runtime diagnostic metadata. It is not persistent.

## Dependencies and integration points
It is consumed by task structures and `irqflags.h` tracing paths.

## Risks and test signals
Risks include stale IP/event tracking and missing compile coverage when tracing is disabled. Tests should cover lockdep reports under IRQ misuse and both tracing-enabled and disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irqflags_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irqhandler.h -->
# sources/distributed-fs/ceph-client/include/linux/irqhandler.h

## Purpose
`irqhandler.h` breaks include cycles by defining the interrupt flow-handler function type used by IRQ descriptors and chips.

## Important APIs, types, and functions
It forward-declares `struct irq_desc` and defines `typedef void (*irq_flow_handler_t)(struct irq_desc *desc)`.

## Control flow
IRQ descriptors store an `irq_flow_handler_t`; dispatch code invokes it to implement level, edge, fasteoi, percpu, nested, or bad interrupt flow.

## State and persistence
The header has no state.

## Dependencies and integration points
It is included by `irq.h`, `irqdomain.h`, `irqdesc.h`, and irqchip drivers to avoid circular dependencies.

## Risks and test signals
Risks are limited to function-signature mismatches and invalid descriptors passed to handlers. Compile coverage across IRQ headers and runtime dispatch tests for each flow handler are sufficient signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irqhandler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irqnr.h -->
# sources/distributed-fs/ceph-client/include/linux/irqnr.h

## Purpose
`irqnr.h` exposes IRQ count/query helpers and iteration macros over descriptors, active IRQs, and numeric IRQ ranges.

## Important APIs, types, and functions
It declares `irq_get_nr_irqs`, `irq_set_nr_irqs`, `irq_to_desc`, and `irq_get_next_irq`, plus macros `for_each_irq_desc`, `for_each_irq_desc_reverse`, `for_each_active_irq`, and `for_each_irq_nr`.

## Control flow
Core and diagnostic code obtain the current IRQ upper bound, resolve descriptors by number, and iterate either all possible numbers, all descriptors, reverse descriptors, or active IRQs.

## State and persistence
The header declares accessors for global IRQ-number state but owns none itself.

## Dependencies and integration points
It depends on UAPI IRQ number definitions and integrates with generic IRQ descriptor storage, proc/debugfs iteration, and kexec/suspend code.

## Risks and test signals
Risks include unsigned/signed reverse iteration corner cases, sparse descriptor NULL handling, and stale upper-bound values. Tests should cover sparse IRQ configs, descriptor allocation beyond legacy IRQs, active IRQ iteration, and reverse iteration at zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irqnr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irqreturn.h -->
# sources/distributed-fs/ceph-client/include/linux/irqreturn.h

## Purpose
`irqreturn.h` defines standard return values for interrupt handlers.

## Important APIs, types, and functions
It defines `enum irqreturn` values `IRQ_NONE`, `IRQ_HANDLED`, and `IRQ_WAKE_THREAD`, typedefs `irqreturn_t`, and provides `IRQ_RETVAL(x)`.

## Control flow
Primary IRQ handlers return these values so the IRQ core can update spurious-interrupt accounting and optionally wake a threaded handler.

## State and persistence
No state exists in the header.

## Dependencies and integration points
It is used by virtually all drivers registering interrupt handlers and by IRQ core action dispatch.

## Risks and test signals
Risks include returning `IRQ_HANDLED` for unrelated shared IRQs, forgetting `IRQ_WAKE_THREAD`, and boolean conversion hiding nuanced outcomes. Tests should cover shared IRQ behavior, threaded IRQ wakeups, spurious interrupt detection, and driver error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/irqreturn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/isa-dma.h -->
# sources/distributed-fs/ceph-client/include/linux/isa-dma.h

## Purpose
`isa-dma.h` includes architecture ISA DMA definitions and exposes the x86 32-bit PCI/ISA DMA bridge bug indicator.

## Important APIs, types, and functions
It includes `<asm/dma.h>` and defines or declares `isa_dma_bridge_buggy`, depending on `CONFIG_PCI && CONFIG_X86_32`.

## Control flow
ISA DMA users can check `isa_dma_bridge_buggy` to decide whether DMA bridge quirks apply. Other builds compile the value as constant zero.

## State and persistence
The only state is the platform global quirk flag when present.

## Dependencies and integration points
It integrates legacy ISA DMA users with architecture DMA APIs and PCI bridge quirk detection.

## Risks and test signals
Risks include code not compiled on non-x86 due to arch DMA assumptions and missing quirk handling on old PCI/ISA systems. Tests should compile x86_32 PCI and non-x86 configs and exercise ISA DMA transfers on affected bridge hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/isa-dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/isa.h -->
# sources/distributed-fs/ceph-client/include/linux/isa.h

## Purpose
`isa.h` defines the small ISA bus driver registration API and module helper macros for legacy devices enumerated by fixed slot/base-index counts.

## Important APIs, types, and functions
It defines `struct isa_driver` with match/probe/remove/shutdown/suspend/resume callbacks, embedded `device_driver`, and devices pointer; `to_isa_driver`; `isa_register_driver`; `isa_unregister_driver`; module init/exit helper macros including IRQ-count validation; and `max_num_isa_dev`.

## Control flow
ISA drivers declare an `isa_driver` and number of devices. Registration creates per-index devices and runs match/probe callbacks. Module macros install init/exit functions, with the IRQ variant validating base and IRQ array counts.

## State and persistence
State is runtime device model state for registered ISA pseudo-devices and driver-owned fixed resources. No persistent state exists.

## Dependencies and integration points
It depends on the device model, errno, kernel logging, module init/exit, and optional `CONFIG_ISA_BUS_API`.

## Risks and test signals
Risks include disabled-config `-ENODEV`, fixed resource collisions, wrong device count, suspend callback misuse, and IRQ count mismatch. Tests should cover registration/probe/remove, module helper validation, disabled config, and multiple legacy ISA device instances.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/isa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/isapnp.h -->
# sources/distributed-fs/ceph-client/include/linux/isapnp.h

## Purpose
`isapnp.h` defines ISA Plug and Play ID encoding macros, card/device ID table structures, low-level configuration accessors, procfs hooks, and compatibility lookup helpers.

## Important APIs, types, and functions
Key macros include `ISAPNP_VENDOR`, `ISAPNP_DEVICE`, `ISAPNP_FUNCTION`, card/device ID initializers, and single-device initializers. `struct isapnp_card_id` describes card and logical devices. APIs include `isapnp_present`, `isapnp_cfg_begin`, `isapnp_cfg_end`, byte read/write, proc init/done, and `pnp_find_dev`, with stubs when ISAPNP is disabled.

## Control flow
Drivers or PnP core encode vendor/device IDs, detect ISA PnP presence, enter configuration mode for a card select number and logical device, read/write config registers, and optionally expose procfs data.

## State and persistence
State is ISA PnP hardware configuration and PnP core device/card objects. Header stubs hold no state.

## Dependencies and integration points
It depends on PnP core and mod_devicetable definitions, and integrates legacy ISA PnP devices with Linux driver matching.

## Risks and test signals
Risks include ID byte-order mistakes, disabled-config fallbacks, config-mode sequencing errors, and procfs coverage. Tests should cover ID macro values, probing with/without ISAPNP, logical device lookup, config read/write, and module ID table matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/isapnp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iscsi_boot_sysfs.h -->
# sources/distributed-fs/ceph-client/include/linux/iscsi_boot_sysfs.h

## Purpose
`iscsi_boot_sysfs.h` defines the common sysfs object model for exporting firmware-discovered iSCSI boot information, including Ethernet, target, initiator, and ACPI table attributes.

## Important APIs, types, and functions
It defines property enums for Ethernet, target, initiator, and ACPI table attributes; `struct iscsi_boot_kobj` with kobject, attribute group, driver data, show/visibility/release callbacks; `struct iscsi_boot_kset`; and create/destroy APIs for ksets and per-object kobjects.

## Control flow
Low-level firmware/table parsers create a boot kset, create indexed Ethernet/target/initiator/ACPI kobjects with callbacks, expose readable attributes depending on `is_visible`, and destroy the kset on teardown. Release callbacks free driver-specific data when the kobject is released.

## State and persistence
State is runtime sysfs kobjects/ksets plus driver-owned parsed boot data. The exported values originate from firmware and are not modified persistently by this API.

## Dependencies and integration points
It integrates with the kernel kobject/sysfs model, iBFT and other boot-firmware parsers, SCSI/iSCSI boot consumers, and host-number-specific sysfs trees.

## Risks and test signals
Risks include kobject lifetime leaks, exposing secrets such as CHAP keys with wrong permissions, callback type mismatches, and destroy while sysfs files are open. Tests should cover attribute visibility, release callback execution, multiple NIC/target entries, host kset naming, and secret permission policy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iscsi_boot_sysfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iscsi_ibft.h -->
# sources/distributed-fs/ceph-client/include/linux/iscsi_ibft.h

## Purpose
`iscsi_ibft.h` declares discovery and reservation support for the iSCSI Boot Firmware Table physical memory region.

## Important APIs, types, and functions
It declares global `phys_addr_t ibft_phys_addr`, conditionally declares `reserve_ibft_region`, and defines the legacy search bounds `IBFT_START` and `IBFT_END` when `CONFIG_ISCSI_IBFT_FIND` is enabled.

## Control flow
Early boot code searches 512 KiB through 1 MiB for the iBFT, reserves the physical region, and records its address in `ibft_phys_addr`. Disabled builds compile `reserve_ibft_region` to a no-op.

## State and persistence
Runtime state is the discovered physical address. The underlying table is firmware-provided memory and persists only according to platform firmware behavior.

## Dependencies and integration points
It depends on physical address types and integrates early memory reservation with iSCSI boot sysfs export.

## Risks and test signals
Risks include missing the table outside legacy bounds, failing to reserve memory before reuse, and disabled configs losing boot data. Tests should cover systems with and without iBFT, memory reservation maps, malformed tables, and disabled finder builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iscsi_ibft.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ism.h -->
# sources/distributed-fs/ceph-client/include/linux/ism.h

## Purpose
`ism.h` defines the IBM Internal Shared Memory device/client interface used by ISM hardware and SMC-D integration.

## Important APIs, types, and functions
It defines `MAX_CLIENTS`, `ISM_NR_DMBS`, `struct ism_dev`, `struct ism_event`, `struct ism_client`, `ism_register_client`, `ism_unregister_client`, `ism_get_priv`, `ism_set_priv`, and `ism_get_smcd_ops`.

## Control flow
Clients register an `ism_client` to receive events. ISM devices maintain per-client private pointers and subscriber slots. Event delivery invokes `handle_event`. SMC-D code can obtain `smcd_ops` from the ISM implementation.

## State and persistence
Runtime state includes device locks, command serialization lock, global device list link, PCI/DIBS pointers, SBA and event-queue DMA addresses, SBA bitmap, per-client private data, event queue index, and subscriber array. No on-disk persistence exists.

## Dependencies and integration points
It depends on workqueue includes, PCI/DIBS/SMC-D types supplied elsewhere, spinlocks, DMA mappings, bitmaps, and client registration code.

## Risks and test signals
Risks include client ID exhaustion, private-pointer misuse, event delivery after unregister, DMA/SBA bitmap leaks, and command-lock deadlocks. Tests should cover max-client registration, event fanout, unregister races, SBA allocation/free, PCI remove, and SMC-D ops availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ism.h -->
