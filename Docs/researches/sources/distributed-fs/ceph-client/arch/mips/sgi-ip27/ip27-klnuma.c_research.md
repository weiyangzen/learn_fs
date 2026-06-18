# sources/distributed-fs/ceph-client/arch/mips/sgi-ip27/ip27-klnuma.c

Purpose: kernel text replication support for IP27 NUMA. It computes which nodes host replicated read-only text and records per-node kernel variable mappings.

Important APIs and control flow: `setup_replication_mask()` always marks node 0 and, under `CONFIG_REPLICATE_KTEXT`, marks all online nodes, then stores the mask in `GDA`. `set_ktext_source()` writes `kern_vars` with magic, read-only NASID, read-write NASID, and base addresses. `copy_kernel()` copies `_stext.._etext` to the destination node. `replicate_kernel_text()` assigns/copies sources for each online node. `node_getfirstfree()` returns the first free PFN accounting for mapped kernels, replicated text, or PROM stack areas.

State, persistence, and integration: state includes `ktext_repmask`, GDA pointer, per-hub `kern_vars`, and copied text pages. Dependencies include mapped-kernel address macros, online node map, and memory initialization. Risks include simplistic placement, memcpy instead of BTE, headless-node concerns noted in comments, and memory layout sensitivity. Test signals are replication logs, correct node first-free PFNs, and successful SMP boot with replicated text enabled.
