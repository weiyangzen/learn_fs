<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/ffa.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/ffa.c

## Purpose
`ffa.c` implements the nVHE/pKVM proxy for Arm FF-A firmware calls made by the host. It intercepts standard FF-A SMCs, rejects unsupported memory-management and messaging calls, forwards safe calls to EL3/SPMD, and wraps share/lend/reclaim operations with host stage-2 ownership checks so the host cannot expose protected guest memory to secure-world firmware.

## Important APIs, Types, and Functions
`struct kvm_ffa_descriptor_buffer` stores a hyp-private descriptor scratch area for fragmented retrieve responses. `struct kvm_ffa_buffers` tracks locked RX/TX mailboxes for the host and hypervisor. `kvm_host_ffa_handler()` is the trap entry point from `hyp-main.c`. `hyp_ffa_init()` probes firmware FF-A support and partitions proxy pages into hyp TX, hyp RX, and descriptor storage. `do_ffa_rxtx_map()` and `do_ffa_rxtx_unmap()` share, pin, unpin, and unshare host mailbox pages. `do_ffa_mem_xfer()`, `do_ffa_mem_frag_tx()`, and `do_ffa_mem_reclaim()` mirror descriptors through hyp buffers and call `__pkvm_host_share_ffa()` / `__pkvm_host_unshare_ffa()` around firmware transactions. `do_ffa_version()`, `do_ffa_features()`, and `do_ffa_part_get()` handle version negotiation, feature discovery, and partition-info copying.

## Control Flow, State, and Persistence
The file maintains persistent hyp state in `hyp_ffa_version`, `has_version_negotiated`, `host_buffers`, `hyp_buffers`, and `ffa_desc_buf`; all RX/TX buffer operations are serialized by `host_buffers.lock`, and version negotiation by `version_lock`. Host calls must negotiate `FFA_VERSION` before other FF-A calls. RXTX map first maps hyp buffers into SPMD, then shares and pins the host pages in hyp; unmap reverses that state. Memory share/lend copies the first fragment into hyp memory, validates descriptor shape and range counts, updates host page state to shared-owned, issues the SMC, and rolls back host state if firmware rejects the transfer. Reclaim retrieves the descriptor from firmware, handles fragments into `ffa_desc_buf`, calls firmware reclaim, then marks pages owned by the host again.

## Dependencies and Integration Points
It depends on Arm SMCCC 1.2 wrappers, Linux FF-A ABI definitions, pKVM ownership helpers from `mem_protect.c`, hyp virtual/physical conversion helpers, and the host SMC trap path in `hyp-main.c`. It also relies on PSCI/SMCCC version information initialized by the host and on setup-provided FF-A proxy pages.

## Risks and Test Signals
Key risks are descriptor parsing bugs from untrusted host TX contents, rollback gaps after partial fragments, stale pinned host mailbox pages, incorrect FF-A version downgrade behavior, and firmware quirks around fragmented retrieve responses. Useful tests include FF-A version negotiation before/after downgrade attempts, RXTX map/unmap error unwind, share/lend with malformed offsets or counts, fragment rollback on firmware failure, reclaim with fragmented descriptors, and verifying host stage-2 page states after each path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/ffa.c -->
