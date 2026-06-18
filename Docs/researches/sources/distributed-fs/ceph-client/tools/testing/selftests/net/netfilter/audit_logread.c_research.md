## sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/audit_logread.c

Purpose: small NETLINK_AUDIT reader used by `nft_audit.sh` to enable audit logging, register itself as the audit listener, normalize netfilter audit messages, and print stable fields for comparison.

Important APIs and types: uses `socket(PF_NETLINK, SOCK_RAW, NETLINK_AUDIT)`, `sendto`, `recvfrom`, `sigaction`, `AUDIT_SET`, `AUDIT_STATUS_ENABLED`, `AUDIT_STATUS_PID`, `AUDIT_NETFILTER_CFG`, `struct audit_status`, and `struct nlmsghdr`.

Control flow: `audit_send()` sends audit control requests with increasing sequence ids. `audit_set()` sends and waits for an ACK. `main()` opens the audit netlink socket, installs SIGTERM/SIGINT cleanup, enables auditing, sets the audit PID to this process, then loops through `readlog()`. `readlog()` ignores non-netfilter audit records, tokenizes message fields, drops variable/uninteresting keys (`pid`, `comm`, `subj`), strips table sequence suffixes, and prints normalized `key=value` fields.

State and persistence: global `fd` identifies the audit socket. Cleanup disables audit and closes the socket; if killed ungracefully, audit state may remain altered until reset elsewhere. Dependencies are audit kernel support and privilege to set audit status. Risks include destructive `strtok()` parsing on kernel-provided text, assuming one audit daemon is not concurrently managing the audit socket, and broad audit disabling on exit. Test signals are normalized stdout lines consumed by shell diffing.
