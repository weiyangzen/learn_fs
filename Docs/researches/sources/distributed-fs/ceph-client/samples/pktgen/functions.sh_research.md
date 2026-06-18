# sources/distributed-fs/ceph-client/samples/pktgen/functions.sh

Purpose: shared Bash library for pktgen sample scripts.

Important APIs/functions: logging helpers `err`, `warn`, `info`; pktgen control helpers `pg_ctrl`, `pg_thread`, `pg_set`, `proc_cmd`, legacy `pgset`; cleanup `trap_exit`; privilege helper `root_check_run_with_sudo`; NUMA/IRQ helpers `get_iface_node`, `get_iface_irqs`, `get_node_cpus`; address/port helpers `validate_addr`, `parse_addr`, `validate_ports`, and IPv6 variants.

Control flow: sourced by pktgen scripts, enables `errexit`, validates `/proc/net/pktgen` control files, writes commands, checks `Result: OK`, and exits on errors. Address helpers parse IPv4/IPv6 and CIDR ranges using shell arithmetic.

State and persistence: exports `PROC_DIR`; scripts modify `/proc/net/pktgen` state and optionally reset it on exit.

Dependencies and integration: requires Bash, root privileges or sudo, pktgen procfs, `/sys/class/net`, `/proc/interrupts`, and standard coreutils.

Risks: shell arithmetic and IPv6 parsing are sample-grade. `set -o errexit` affects callers. Commands write directly to pktgen proc files and can disrupt active generator state.

Test signals: source from pktgen scripts, run with `-x` for debug, verify invalid addresses/ports fail, and confirm pktgen proc writes report OK.
