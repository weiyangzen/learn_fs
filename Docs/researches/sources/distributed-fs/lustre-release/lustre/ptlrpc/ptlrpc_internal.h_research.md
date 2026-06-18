# sources/distributed-fs/lustre-release/lustre/ptlrpc/ptlrpc_internal.h

Purpose: internal PTLRPC header that shares declarations and inline helpers across the PTLRPC implementation without exposing them as public Lustre APIs.

Important APIs/types/functions: declares global service/NRS state, NRS policy configs, `ptlrpcd_start()`, client request cache and resend helpers, portal init/fini, recovery helpers, lproc/sysfs service hooks, NRS core operations, pinger lifecycle, security PTLRPC module lifecycle, target/nodemap server module hooks, and pack helpers. Inline helpers include `nrs_svcpt_has_hp()`, `nrs_svc_has_hp()`, `nrs_svcpt2nrs()`, `nrs_pol2cptid()`, `nrs_pol2svc()`, `nrs_pol2svcpt()`, `nrs_pol2cptab()`, `nrs_request_resource()`, `nrs_request_policy()`, `ptlrpc_recoverable_error()`, request initialization helpers, connect/disconnect opcode predicates, and `do_pack_body()`.

Control flow: the header encodes common access patterns used by service code and NRS policies. Request initialization sets locks, refcounts, lists, wait queues, and role-specific flags before request objects enter client or server flows. NRS inline helpers translate between policy, service partition, CPT, and resource objects. `do_pack_body()` populates MDT body identity/capability fields for set-info style requests.

State/persistence: no direct storage beyond external declarations. The inline initializers establish in-memory request state contracts; misuse can leave list heads, wait queues, or refcounts uninitialized.

Dependencies/integration: ties together LDLM internals, heap support, Lustre compatibility headers, request capsules, PTLRPC daemon, pinger, security, NRS, lprocfs/sysfs, target, nodemap, client, service, and event modules.

Risks/test signals: changes here have broad blast radius because many C files rely on the exact initialization and inline accessor contracts. Tests should cover client/server request allocation paths, NRS policy resource selection, HP queue detection, connect/disconnect classification, recovery error predicates, and set-info body packing with current credentials.
