# sources/distributed-fs/ceph-client/tools/sched/root_domains_dump.py

Purpose: drgn diagnostic that prints unique scheduler root domains and their CPU masks.

Important APIs/functions: `print_root_domains_info()` reads `prog['runqueues']` and `prog['def_root_domain']`, iterates possible CPUs, gets `rq.rd`, de-duplicates root-domain pointers in `seen_root_domains`, and prints the first CPU seen plus cpumask strings through `cpumask_to_cpulist()`.

Control flow: argparse sets help text, then the root-domain printer walks per-CPU runqueues. It labels the default root domain specially when the pointer equals `def_root_domain.address_`; other root domains are printed by address. Fault, attribute, and generic exceptions are reported per CPU.

State and persistence: no persistent state. Runtime state is only the set of already printed root-domain addresses.

Dependencies and integration: requires drgn and scheduler symbols/BTF for runqueues, root domains, and cpumask helpers. It is useful for cpuset, CPU hotplug, and scheduling-domain debugging.

Risks: the script prints both `Span` and `Online` from `root_domain.span[0]`; this appears suspicious because a separate online mask may exist or the label may be misleading. Pointer conversion with `int(root_domain)` depends on drgn object behavior. Kernel field changes can break access.

Test signals: run on a normal single-root-domain system, then with cpuset partitions or hotplug configurations that create multiple root domains; verify that duplicate pointers are suppressed and masks match scheduler debugfs expectations.
