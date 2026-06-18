
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_queue.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_queue.c

## Purpose

`nft_queue.c` implements the nftables `queue` expression, which returns an `NF_QUEUE` verdict to send matching packets to nfnetlink_queue userspace consumers. It supports fixed queue numbers, register-supplied queue numbers, queue ranges, hash-based load distribution, CPU fanout, and bypass behavior.

## Important APIs, Types, and Functions

`struct nft_queue` stores queue register, base queue number, queue count, and flags. `nft_queue_eval()` handles fixed/ranged queues and uses either CPU modulo fanout or `nfqueue_hash()`. `nft_queue_sreg_eval()` uses a runtime queue id from `regs->data`. `nft_queue_validate()` restricts families and hooks to places with a queue continuation path. `nft_queue_select_ops()` chooses fixed or source-register operations and initializes `jhash_initval`.

## Control Flow

Rule creation rejects ambiguous fixed and register queue attributes. Fixed queue initialization validates `queues_total`, computes the highest queue id, checks `U16_MAX`, and stores optional flags. Register-based initialization validates a 32-bit register load and disallows CPU fanout because there is no static queue range. Evaluation computes the queue id, wraps it in `NF_QUEUE_NR()`, ORs bypass when configured, and writes the verdict code.

## State and Persistence Behavior

Expression configuration persists in `struct nft_queue`. The only global state is the read-mostly `jhash_initval` seed, initialized when operations are selected. Runtime evaluation does not retain packet state beyond setting `regs->verdict.code`.

## Dependencies and Integration Points

The module registers `nft_queue_type` with nf_tables and integrates with `nf_queue.h`, `nfqueue_hash()`, netfilter verdict encoding, and nfnetlink_queue userspace listeners. It supports IPv4, IPv6, inet, and bridge families but rejects netdev.

## Risks and Test Signals

Risks include invalid queue range arithmetic, unsupported hook placement, and queue bypass policy surprises when no userspace listener is present. Test with fixed queues, register queues, multi-queue fanout, CPU fanout, bypass enabled/disabled, bridge family rules, and attempts to attach queue rules to netdev ingress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_queue.c -->
