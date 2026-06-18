# sources/distributed-fs/ceph-client/arch/sparc/kernel/mdesc.c

Purpose: Manages sun4v machine descriptions from the hypervisor, exposing graph traversal, dynamic update notifications, CPU topology extraction, page-size discovery, and `/dev/mdesc` reads.

Important APIs/types/functions: `struct mdesc_hdr` and `struct mdesc_elem` define the hypervisor-provided node/name/data layout. `struct mdesc_handle` wraps aligned description bytes with refcounting and allocation ops. Exported traversal APIs include `mdesc_grab()`, `mdesc_release()`, `mdesc_register_notifier()`, `mdesc_update()`, `mdesc_get_node()`, `mdesc_get_node_info()`, `mdesc_node_by_name()`, `mdesc_get_property()`, `mdesc_next_arc()`, `mdesc_arc_target()`, and `mdesc_node_name()`. CPU/platform routines include `sun4v_mdesc_init()`, `mdesc_populate_present_mask()`, `mdesc_get_page_sizes()`, and `mdesc_fill_in_cpu_data()`.

Control flow: Early boot calls `sun4v_mdesc_init()`, asks the hypervisor for the size and bytes, allocates through memblock, installs `cur_mdesc`, initializes ADI, and reports platform properties. Later `mdesc_update()` rereads through kmalloc, swaps `cur_mdesc`, computes notifier remove/add events for supported node types, and retains old referenced handles on a zombie list. Traversal helpers walk the flat element table, matching node tags, property names, and arc types.

State and persistence: Persistent runtime state is `cur_mdesc`, handle refcounts, `mdesc_zombie_list`, notifier client list, `max_cpus`, and populated `cpu_data`/trap-block fields. `/dev/mdesc` open pins a handle until close, making reads stable across updates.

Dependencies and integration points: It depends on sun4v hypervisor `sun4v_mach_desc`, memblock/kmalloc, refcounts, Open Firmware string-list helpers, CPU masks/topology, trap queue sizing, ADI initialization, miscdevice registration, and LDC/virtual-device clients that register MD notifiers.

Risks and test signals: Node comparison currently supports only virtual-device-port and domain-services-port clients. Graph traversal must tolerate cycles via bounded recursion in back-node searches. Tests include boot MD parsing, `/dev/mdesc` read/seek across updates, notifier add/remove on virtual device changes, CPU topology/cache/socket IDs, page-size mask intersection, missing platform properties, and refcount/zombie cleanup.
